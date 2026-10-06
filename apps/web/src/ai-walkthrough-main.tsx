import { createRoot } from "react-dom/client";
import { AIFictionalWalkthrough } from "./AIFictionalWalkthrough";

const target = document.getElementById("root");
if (!target) throw new Error("Walkthrough root unavailable");
createRoot(target).render(<AIFictionalWalkthrough />);
