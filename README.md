# RPIGames
Full-Stack Web App for Playing Games on the RPI Campus

## Developer quick start

- backend code can be found at `src/backend`
  - get yourself into a venv with [the requirements](src/backend/requirements.txt)
  - start development server with `fastapi dev`
- frontend code can be found at `src/frontend`
  - get typescript with npm
  - you can compile the typescript to js with `tsc -p .` in the `src/frontend` folder
  - you can also start a nginx frontend server (that also links to the
  backend fastapi development port) using the [start](quick_frontend_start.sh) and
  [stop](quick_frontend_stop.sh) scripts

When packaging, use the docker scripts to ensure reproducibility.
