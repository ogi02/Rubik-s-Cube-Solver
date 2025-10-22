import p5 from "p5";
import { cubeSketch } from "./sketch/sketch";

// Initialize the p5 sketch in the HTML element with id "visualizer"
new p5(cubeSketch, document.getElementById("visualizer") as HTMLElement);