import shutil
import subprocess
import tempfile
import sys
import importlib.util
from pathlib import Path
from typing import Any, Type, cast

import docker
from jinja2 import Environment, FileSystemLoader

from definable.utils.yaml_parser import ConfigParser
from definable.base.agent import AgentBox


class DockerBuilder:
    def __init__(self, config_path: str = "agent.yaml") -> None:
        self.config = ConfigParser.load_config(config_path)
        self.docker_client = docker.from_env()

    def build_image(self, tag: str, context_path: str = ".", verbose: bool = False) -> Any:
        """Build Docker image for the agent using docker-compose"""
        # Create temporary build context
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_obj.name

        try:
            # Copy source files
            self._copy_source_files(context_path, temp_dir)

            # Validate agent implementation before building
            print("🔍 Validating agent implementation...")
            self._validate_agent(context_path)

            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile()
            dockerfile_path = Path(temp_dir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)

            # Generate requirements.txt
            requirements_content = self._generate_requirements()
            requirements_path = Path(temp_dir) / "requirements.txt"
            requirements_path.write_text(requirements_content)

            # Generate docker-compose.yml
            docker_compose_content = self._generate_docker_compose(tag)
            docker_compose_path = Path(temp_dir) / "docker-compose.yml"
            docker_compose_path.write_text(docker_compose_content)

            # Copy .dockerignore
            dockerignore_path = (
                Path(__file__).parent.parent / "templates" / ".dockerignore"
            )
            if dockerignore_path.exists():
                shutil.copy2(dockerignore_path, Path(temp_dir) / ".dockerignore")

            # Build image using docker-compose
            print(f"Building Docker image with docker-compose: {tag}")
            self._run_docker_compose_build(temp_dir, tag, verbose)

            # Clean up dangling images after build
            self._cleanup_dangling_images()

            # Return a simple object with the tag (maintaining interface compatibility)
            return type('BuildResult', (), {'id': tag, 'tags': [tag]})()

        finally:
            # Clean up temporary directory
            # temp_dir_obj.cleanup()
            pass

    def _validate_agent(self, context_path: str) -> None:
        """Validate that the agent implementation is correct"""
        try:
            # Get agent module and class info
            module_file, class_name = ConfigParser.get_agent_class_info(self.config.agent)
            
            # Add context path to sys.path so local modules can be imported
            context_path_added = False
            abs_context_path = str(Path(context_path).resolve())
            if abs_context_path not in sys.path:
                sys.path.insert(0, abs_context_path)
                context_path_added = True
            
            try:
                # Extract module name from file path (e.g., "main.py" -> "main")
                module_name = Path(module_file).stem
                
                # Create a temporary package to enable relative imports
                # We'll pretend the agent directory is a package called "agent_pkg"
                package_name = "agent_pkg"
                full_module_name = f"{package_name}.{module_name}"
                
                # Create the parent package if it doesn't exist
                if package_name not in sys.modules:
                    package_spec = importlib.util.spec_from_loader(package_name, loader=None)
                    package_module = importlib.util.module_from_spec(package_spec)
                    package_module.__path__ = [abs_context_path]  # Set package path
                    sys.modules[package_name] = package_module
                
                # Now import the module as part of the package
                spec = importlib.util.spec_from_file_location(
                    full_module_name, 
                    str(Path(abs_context_path) / module_file),
                    submodule_search_locations=[]
                )
                module = importlib.util.module_from_spec(spec)
                module.__package__ = package_name  # Set package context for relative imports
                sys.modules[full_module_name] = module
                spec.loader.exec_module(module)
                
            finally:
                # Clean up sys.path modification and temporary modules
                if context_path_added and abs_context_path in sys.path:
                    sys.path.remove(abs_context_path)
                
                # Clean up temporary modules from sys.modules
                modules_to_remove = [name for name in sys.modules.keys() if name.startswith("agent_pkg")]
                for module_name in modules_to_remove:
                    del sys.modules[module_name]

            # Get the agent class and instantiate
            agent_class = cast(Type[AgentBox], getattr(module, class_name))
            agent_instance = agent_class()
            agent_instance._ensure_setup()
            
            # Validate that at least one execution method is implemented
            agent_instance.validate_implementation()
            
            print(f"✅ Agent validation successful!")
            
        except Exception as e:
            print(f"❌ Agent validation failed: {str(e)}")
            raise Exception(f"Agent validation failed: {str(e)}")

    def _cleanup_dangling_images(self) -> None:
        """Remove dangling images created during build"""
        try:
            # Get dangling images
            dangling_images = self.docker_client.images.list(filters={"dangling": True})

            if dangling_images:
                print(f"Cleaning up {len(dangling_images)} dangling images...")
                for image in dangling_images:
                    try:
                        self.docker_client.images.remove(image.id, force=True)
                    except Exception:
                        pass  # Ignore errors during cleanup

        except Exception:
            pass  # Ignore cleanup errors

    def _copy_source_files(self, source_path: str, dest_path: str) -> None:
        """Copy source files to build context"""
        source = Path(source_path)
        dest = Path(dest_path)

        # Copy Python files and YAML config
        for file_pattern in ["*.py", "*.yaml", "*.yml"]:
            for file_path in source.glob(file_pattern):
                shutil.copy2(file_path, dest / file_path.name)

        # Copy directories (like models, data, etc.)
        for item in source.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                shutil.copytree(item, dest / item.name)

    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile from template"""
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("Dockerfile.jinja2")

        return template.render(
            python_version=self.config.build.python_version,
            system_packages=self.config.build.system_packages,
            environment_variables=self.config.build.environment_variables,
            platform_name=self.config.platform.name,
        )

    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("requirements.txt.jinja2")

        return template.render(dependencies=self.config.build.dependencies)

    def _generate_docker_compose(self, image_tag: str) -> str:
        """Generate docker-compose.yml from template"""
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("docker-compose.yml.jinja2")

        return template.render(
            platform_name=self.config.platform.name,
            image_tag=image_tag,
            environment_variables=self.config.build.environment_variables,
        )

    def _run_docker_compose_build(self, build_dir: str, tag: str, verbose: bool = False) -> None:
        """Run docker-compose build and handle output"""
        try:
            # Run docker-compose build
            process = subprocess.Popen(
                ["docker-compose", "build", "--no-cache"],
                cwd=build_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Process output in real-time
            current_step = 0
            total_steps = 0
            
            if process.stdout is None:
                raise Exception("Failed to capture build output")
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if not line:
                    continue

                if verbose:
                    # In verbose mode, show all logs
                    print(line)
                else:
                    # In normal mode, filter logs to show only important information
                    # Parse docker build output from docker-compose
                    if "Step " in line and "/" in line:
                        # Extract step information
                        if "Step 1/" in line:
                            total_steps = int(line.split("/")[1].split(" ")[0])
                        
                        if line.startswith("Step "):
                            step_parts = line.split(" ")
                            if len(step_parts) >= 2 and "/" in step_parts[1]:
                                current_step = int(step_parts[1].split("/")[0])
                                step_name = line.split(" : ")[1] if " : " in line else "Unknown"
                                print(f"[{current_step}/{total_steps}] {step_name}")
                            else:
                                print(line)
                        else:
                            print(line)
                    
                    # Show important messages
                    elif any(keyword in line.upper() for keyword in ["ERROR", "SUCCESS", "BUILT", "TAGGED"]):
                        print(line)
                    
                    # Show warnings but make them less prominent
                    elif "WARNING" in line.upper() and "pip" not in line.lower():
                        print(f"⚠️  {line}")
                    
                    # Show building service messages
                    elif "Building" in line or "Creating" in line:
                        print(line)

            # Wait for process to complete
            process.wait()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, "docker-compose build")
                
            print(f"✅ Successfully built {tag}")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Docker compose build failed with return code {e.returncode}")
        except FileNotFoundError:
            raise Exception("docker-compose command not found. Please install Docker Compose.")
        except Exception as e:
            raise Exception(f"Build failed: {str(e)}")
