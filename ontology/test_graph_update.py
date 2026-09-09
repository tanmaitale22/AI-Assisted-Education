from daa_graph_builder import build_daa_graph


# --------------------------------
# First knowledge extraction
# --------------------------------

knowledge_1 = {

    "nodes": [

        {
            "name": "Merge Sort",
            "type": "Algorithm"
        },

        {
            "name": "Divide and Conquer",
            "type": "Technique"
        }

    ],

    "relationships": [

        {
            "source": "Merge Sort",
            "relation": "uses",
            "target": "Divide and Conquer"
        }

    ]
}


# --------------------------------
# Second knowledge extraction
# --------------------------------

knowledge_2 = {

    "nodes": [

        {
            "name": "Merge Sort",
            "type": "Algorithm"
        },

        {
            "name": "Sorting",
            "type": "Concept"
        }

    ],

    "relationships": [

        {
            "source": "Merge Sort",
            "relation": "uses",
            "target": "Divide and Conquer"
        },

        {
            "source": "Merge Sort",
            "relation": "relatedTo",
            "target": "Sorting"
        }

    ]
}


print("\n===== FIRST UPDATE =====\n")

build_daa_graph(knowledge_1)


print("\n===== SECOND UPDATE =====\n")

build_daa_graph(knowledge_2)