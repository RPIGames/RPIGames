# RPIGames
Full-Stack Web App for Playing Games on the RPI Campus

## Developer quick start

- backend code can be found at `src/backend`
  - we use `uv` as a project manager in our backend
  - use the `./quick_backend_run.sh` script
  - or start development server with `fastapi dev` after installing the requirements
- frontend code can be found at `src/frontend`
  - get `tsc` with npm or your package manager (package name `typescript` on some linux distros.)
  - you can compile the typescript to js with `tsc -p .` in the `src/frontend` folder
    - this has been made automatic with `./compile_typescript.sh`
  - you can also start a nginx frontend server (that also links to the
  backend fastapi development port) using the [start](quick_frontend_start.sh) and
  [stop](quick_frontend_stop.sh) scripts

When packaging, use the docker scripts to ensure reproducibility.
