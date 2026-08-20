# Rubik-s-Cube-Solver
Thesis Project

## Running with Docker

`docker-compose.yml` builds and runs the WebSocket server, the visualizer and the demo client.

Bring up the server and the visualizer:

```bash
docker compose up -d --build
```

The visualizer is served on [http://localhost:5173](http://localhost:5173) and the server listens on
port `8080`.

Open the visualizer in a browser, then run the demo client, which scrambles a cube, solves it and
drives the animation:

```bash
docker compose run --rm playground
```

The demo client sits behind the `demo` profile, so `docker compose up` never starts it before the
visualizer page is open.

Stop everything with:

```bash
docker compose down
```

### Configuration

| Variable | Default | Used by |
| --- | --- | --- |
| `JWT_SECRET` | `dev-secret` | server |
| `SOLVER_API_KEY` | `solver` | server, demo client |
| `VISUALIZER_API_KEY` | `visualizer` | server, visualizer |
| `VITE_SERVER_URL` | `http://localhost:8080` | visualizer |

The defaults are development values that let `docker compose up` work out of the box. Override them
by exporting them in the shell or by writing a `.env` file at the repository root.

The visualizer values are inlined into its bundle by Vite at build time, so changing
`VISUALIZER_API_KEY` or `VITE_SERVER_URL` requires a rebuild:

```bash
docker compose build visualizer
```
