"""
Bootstraps an application from a remote github repository given environment variables.

This just sets up the files from the repository. It's more of a build process, does not start an application.
"""

import asyncio
from llama_deploy.core.git.git_util import (
    clone_repo,
)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BootstrapSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLAMA_DEPLOY_")
    git_url: str = Field(..., description="The URL of the git repository to clone")
    git_token: str | None = Field(
        default=None, description="The token to use to clone the git repository"
    )
    git_ref: str | None = Field(
        default=None, description="The git reference to checkout"
    )
    git_sha: str | None = Field(default=None, description="The git SHA to checkout")
    deployment_file_path: str = Field(
        default="llama_deploy.yaml", description="The path to the deployment file"
    )
    deployment_name: str | None = Field(
        default=None, description="The name of the deployment"
    )


async def main():
    settings = BootstrapSettings()
    # Needs the github url+auth, and the deployment file path
    # clones the repo to a standard directory
    # (eventually) runs the UI build process and moves that to a standard directory for a file server
    clone_repo(settings.git_url, "/app/", settings.git_token)
    pass


if __name__ == "__main__":
    asyncio.run(main())
