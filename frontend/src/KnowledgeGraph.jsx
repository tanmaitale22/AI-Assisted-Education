import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import "./App.css";
 

function KnowledgeGraph() {
  const containerRef = useRef(null);

  useEffect(() => {
    let cy;

    const loadGraph = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/knowledge-graph"
        );

        const graphData = await response.json();

        cy = cytoscape({
          container: containerRef.current,

          elements: [
            ...graphData.nodes,
            ...graphData.edges
          ],

          style: [
            {
              selector: "node",
              style: {
                label: "data(label)",
                width: 100,
                height: 60,

                "text-valign": "center",
                "text-halign": "center",

                "font-size": "12px",
                "text-wrap": "wrap",
                "text-max-width": "90px",

                "background-color": "#6366f1",
                color: "#ffffff"
              }
            },

            {
              selector: "edge",
              style: {
                width: 2,

                label: "data(label)",
                "font-size": "10px",

                "curve-style": "bezier",

                "target-arrow-shape": "triangle",

                "line-color": "#94a3b8",
                "target-arrow-color": "#94a3b8",

                color: "#475569",
                "text-background-color": "#ffffff",
                "text-background-opacity": 1,
                "text-background-padding": "3px"
              }
            }
          ],

          layout: {
            name: "cose",

            animate: false,

            padding: 100,

            idealEdgeLength: 150,

            nodeRepulsion: 8000,

            gravity: 0.3
          }
        });

        // Make Cytoscape automatically zoom
        // to properly fill the available space
        setTimeout(() => {
          cy.fit(undefined, 80);
          cy.center();
        }, 300);

      } catch (error) {
        console.error(
          "Failed to load knowledge graph:",
          error
        );
      }
    };

    loadGraph();

    return () => {
      if (cy) {
        cy.destroy();
      }
    };
  }, []);

  return (
    <div className="knowledge-graph-page">
      <div className="knowledge-graph-container">

        <h2>DAA Knowledge Graph</h2>

        <div
          ref={containerRef}
          className="cytoscape-container"
        />

      </div>
    </div>
  );
}

export default KnowledgeGraph;