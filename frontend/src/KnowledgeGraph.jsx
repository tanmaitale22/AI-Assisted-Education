import { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";
import "./App.css";
 

function KnowledgeGraph() {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);

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

        cy.on("tap", "node", async (event) => {
          const node = event.target;

          const nodeName = node.data("label");
          console.log("CLICKED NODE:", nodeName);

          const response = await fetch(
            `http://127.0.0.1:8000/knowledge-graph/node/${encodeURIComponent(nodeName)}`
          );

          const data = await response.json();

          console.log("NODE CONTEXT:", data);

          setSelectedNode({
            name: nodeName,
            chunks: data.chunks
          });
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

      {selectedNode && (
        <div className="node-details-panel">

          <h2>{selectedNode.name}</h2>

          <h3>Study Material</h3>

          {selectedNode.chunks.length === 0 ? (
            <p>No matching study material found.</p>
          ) : (
            selectedNode.chunks.map((chunk, index) => (
              <div className="chunk-card" key={index}>

                <p>
                  {chunk.content}
                </p>

                <small>
                  Topic: {chunk.topic}
                </small>

                <br />

                <small>
                  Subtopic: {chunk.subtopic}
                </small>

              </div>
            ))
          )}

        </div>
      )}

    </div>
  );
}

export default KnowledgeGraph;