"""
ReproLab Server Extension

This module provides the server-side functionality for the ReproLab JupyterLab extension.
It handles experiment creation, environment management, and data archiving.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path

from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
from jupyter_server.utils import url_path_join
from tornado import web

# Import actual ReproLab functions
from reprolab.experiment.create_experiment import start_experiment, end_experiment
from reprolab.environment.environment import create_new_venv, freeze_venv_dependencies
from reprolab.experiment.archive_file import download_reproducability_package, list_and_sort_git_tags

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('reprolab.server')

class ReprolabHandler(ExtensionHandlerMixin, APIHandler):
    """Base handler for ReproLab API."""
    
    def initialize(self, name=None, **kwargs):
        """Initialize the handler with the extension name."""
        logger.info(f"[ReproLab] Initializing ReprolabHandler with name: {name}")
        super().initialize(name=name or "reprolab", **kwargs)
        logger.info(f"[ReproLab] ReprolabHandler initialized successfully")
    
    @web.authenticated
    def get(self):
        """Get server extension status."""
        logger.info("[ReproLab] Status endpoint called")
        print("[ReproLab Debug] Status endpoint called")
        
        response_data = {
            "status": "success",
            "message": "ReproLab server extension is running",
            "timestamp": datetime.now().isoformat(),
            "debug": "Server extension is working!"
        }
        
        logger.info(f"[ReproLab] Returning status response: {response_data}")
        self.finish(response_data)
    
    def check_xsrf_cookie(self):
        """Disable XSRF check for API endpoints."""
        logger.debug("[ReproLab] XSRF check disabled for API endpoints")
        pass


class ExperimentHandler(ReprolabHandler):
    """Handler for experiment operations."""
    
    @web.authenticated
    def post(self):
        """Create a new experiment."""
        logger.info("[ReproLab] Experiment endpoint called")
        print("[ReproLab Debug] Experiment endpoint called")
        
        try:
            data = json.loads(self.request.body)
            action = data.get('action', 'start')
            logger.info(f"[ReproLab] Experiment action: {action}")
            print(f"[ReproLab Debug] Action: {action}")
            
            # Call actual experiment functions
            if action == 'start':
                logger.info("[ReproLab] Calling start_experiment()")
                tag_name = start_experiment()
                if tag_name:
                    response_data = {
                        "status": "success",
                        "message": f"Experiment started successfully with tag: {tag_name}",
                        "tag_name": tag_name,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    response_data = {
                        "status": "error",
                        "message": "Failed to start experiment",
                        "timestamp": datetime.now().isoformat()
                    }
            elif action == 'end':
                logger.info("[ReproLab] Calling end_experiment()")
                tag_name = end_experiment()
                if tag_name:
                    response_data = {
                        "status": "success",
                        "message": f"Experiment ended successfully with tag: {tag_name}",
                        "tag_name": tag_name,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    response_data = {
                        "status": "error",
                        "message": "Failed to end experiment",
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                response_data = {
                    "status": "error",
                    "message": f"Unknown experiment action: {action}",
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info(f"[ReproLab] Experiment response: {response_data}")
            self.finish(response_data)
            
        except Exception as e:
            logger.error(f"[ReproLab] Experiment error: {str(e)}")
            print(f"[ReproLab Debug] Error: {str(e)}")
            self.set_status(500)
            self.finish({
                "status": "error",
                "message": f"Failed to perform experiment action: {str(e)}"
            })


class EnvironmentHandler(ReprolabHandler):
    """Handler for environment operations."""
    
    @web.authenticated
    def post(self):
        """Create environment files."""
        logger.info("[ReproLab] Environment endpoint called")
        print("[ReproLab Debug] Environment endpoint called")
        
        try:
            data = json.loads(self.request.body)
            action = data.get('action')
            logger.info(f"[ReproLab] Environment action: {action}")
            print(f"[ReproLab Debug] Environment action: {action}")
            
            # Call actual environment functions
            if action == 'create_environment':
                logger.info("[ReproLab] Calling create_new_venv()")
                venv_name = data.get('venv_name', 'my_venv')
                create_new_venv(venv_name)
                response_data = {
                    "status": "success",
                    "message": f"Virtual environment '{venv_name}' created successfully",
                    "venv_name": venv_name,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == 'freeze_dependencies':
                logger.info("[ReproLab] Calling freeze_venv_dependencies()")
                venv_name = data.get('venv_name', 'my_venv')
                freeze_venv_dependencies(venv_name)
                response_data = {
                    "status": "success",
                    "message": f"Dependencies frozen successfully for '{venv_name}'",
                    "venv_name": venv_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                response_data = {
                    "status": "error",
                    "message": f"Unknown environment action: {action}",
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info(f"[ReproLab] Environment response: {response_data}")
            self.finish(response_data)
            
        except Exception as e:
            logger.error(f"[ReproLab] Environment error: {str(e)}")
            print(f"[ReproLab Debug] Error: {str(e)}")
            self.set_status(500)
            self.finish({
                "status": "error",
                "message": f"Failed to perform environment action: {str(e)}"
            })


class ArchiveHandler(ReprolabHandler):
    """Handler for archive operations."""
    
    @web.authenticated
    def post(self):
        """Create an archive package."""
        logger.info("[ReproLab] Archive endpoint called")
        print("[ReproLab Debug] Archive endpoint called")
        
        try:
            data = json.loads(self.request.body)
            tag_name = data.get('tag_name')
            logger.info(f"[ReproLab] Archive tag: {tag_name}")
            print(f"[ReproLab Debug] Archive tag: {tag_name}")
            
            if not tag_name:
                response_data = {
                    "status": "error",
                    "message": "Tag name is required for archive creation",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Call actual archive function
                logger.info(f"[ReproLab] Calling download_reproducability_package() for tag: {tag_name}")
                package_path = download_reproducability_package(tag_name)
                response_data = {
                    "status": "success",
                    "message": f"Archive created successfully for tag: {tag_name}",
                    "package_path": package_path,
                    "tag_name": tag_name,
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info(f"[ReproLab] Archive response: {response_data}")
            self.finish(response_data)
            
        except Exception as e:
            logger.error(f"[ReproLab] Archive error: {str(e)}")
            print(f"[ReproLab Debug] Error: {str(e)}")
            self.set_status(500)
            self.finish({
                "status": "error",
                "message": f"Failed to create archive: {str(e)}"
            })


class ZenodoHandler(ReprolabHandler):
    """Handler for Zenodo integration."""
    
    @web.authenticated
    def post(self):
        """Create Zenodo-ready package."""
        logger.info("[ReproLab] Zenodo endpoint called")
        print("[ReproLab Debug] Zenodo endpoint called")
        
        try:
            data = json.loads(self.request.body)
            tag_name = data.get('tag_name')
            logger.info(f"[ReproLab] Zenodo tag: {tag_name}")
            print(f"[ReproLab Debug] Zenodo tag: {tag_name}")
            
            if not tag_name:
                # Get available tags if no specific tag provided
                logger.info("[ReproLab] No tag provided, getting available tags")
                available_tags = list_and_sort_git_tags()
                response_data = {
                    "status": "success",
                    "message": "Available tags retrieved",
                    "available_tags": available_tags,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Create Zenodo package for specific tag
                logger.info(f"[ReproLab] Creating Zenodo package for tag: {tag_name}")
                package_path = download_reproducability_package(tag_name)
                response_data = {
                    "status": "success",
                    "message": "Zenodo-ready package created successfully",
                    "package_path": package_path,
                    "tag_name": tag_name,
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info(f"[ReproLab] Zenodo response: {response_data}")
            self.finish(response_data)
            
        except Exception as e:
            logger.error(f"[ReproLab] Zenodo error: {str(e)}")
            print(f"[ReproLab Debug] Error: {str(e)}")
            self.set_status(500)
            self.finish({
                "status": "error",
                "message": f"Failed to create Zenodo package: {str(e)}"
            })


def _jupyter_server_extension_paths():
    """Return server extension paths."""
    logger.info("[ReproLab] _jupyter_server_extension_paths called")
    print("[ReproLab Debug] _jupyter_server_extension_paths called")
    
    paths = [
        {
            "module": "reprolab.server"
        }
    ]
    
    logger.info(f"[ReproLab] Server extension paths: {paths}")
    return paths


def _jupyter_labextension_paths():
    """Return labextension paths."""
    logger.info("[ReproLab] _jupyter_labextension_paths called")
    print("[ReproLab Debug] _jupyter_labextension_paths called")
    
    paths = [
        {
            "src": "labextension",
            "dest": "reprolab"
        }
    ]
    
    logger.info(f"[ReproLab] Lab extension paths: {paths}")
    return paths


def load_jupyter_server_extension(server_app):
    """Load the JupyterLab server extension."""
    logger.info("[ReproLab] load_jupyter_server_extension called")
    print("[ReproLab Debug] load_jupyter_server_extension called")
    print(f"[ReproLab Debug] Server app: {server_app}")
    
    try:
        web_app = server_app.web_app
        base_url = web_app.settings['base_url']
        logger.info(f"[ReproLab] Base URL: {base_url}")
        print(f"[ReproLab Debug] Base URL: {base_url}")
        
        # Register the extension name in server settings
        web_app.settings['reprolab'] = server_app
        
        # Add API routes
        handlers = [
            (url_path_join(base_url, 'reprolab', 'api', 'status'), ReprolabHandler),
            (url_path_join(base_url, 'reprolab', 'api', 'experiment'), ExperimentHandler),
            (url_path_join(base_url, 'reprolab', 'api', 'environment'), EnvironmentHandler),
            (url_path_join(base_url, 'reprolab', 'api', 'archive'), ArchiveHandler),
            (url_path_join(base_url, 'reprolab', 'api', 'zenodo'), ZenodoHandler),
        ]
        
        logger.info(f"[ReproLab] Adding handlers: {handlers}")
        print(f"[ReproLab Debug] Adding handlers: {handlers}")
        
        web_app.add_handlers('.*$', handlers)
        
        logger.info("[ReproLab] Server extension loaded successfully")
        print("[ReproLab Debug] Server extension loaded successfully")
        server_app.log.info("ReproLab server extension loaded successfully")
        
    except Exception as e:
        logger.error(f"[ReproLab] Error loading server extension: {str(e)}")
        print(f"[ReproLab Debug] Error loading server extension: {str(e)}")
        raise 
