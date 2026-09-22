from owlready2 import *
import os


# --------------------------------
# Create ontology
# --------------------------------

onto = get_ontology(
    "http://example.org/daa_ontology.owl"
)


with onto:

    # --------------------------------
    # Classes (Node Types)
    # --------------------------------

    class Subject(Thing):
        pass


    class Topic(Thing):
        pass


    class Concept(Thing):
        pass


    class Algorithm(Concept):
        pass


    class DataStructure(Concept):
        pass


    class Problem(Concept):
        pass


    class Technique(Concept):
        pass


    # --------------------------------
    # Relationships (Edge Types)
    # --------------------------------

    class hasTopic(ObjectProperty):
        domain = [Subject]
        range = [Topic]


    class hasSubtopic(ObjectProperty):
        domain = [Topic]
        range = [Concept]


    class belongsTo(ObjectProperty):
        domain = [Concept]
        range = [Topic]


    class uses(ObjectProperty):
        domain = [Concept]
        range = [Concept]


    class solves(ObjectProperty):
        domain = [Algorithm]
        range = [Problem]


    class requires(ObjectProperty):
        domain = [Concept]
        range = [Concept]


    class relatedTo(ObjectProperty):
        domain = [Concept]
        range = [Concept]
        symmetric = True


# --------------------------------
# Save ontology
# --------------------------------


if __name__ == "__main__":

    current_directory = os.path.dirname(
        os.path.abspath(__file__)
    )

    ontology_path = os.path.join(
        current_directory,
        "daa_ontology.owl"
    )

    onto.save(
        file=ontology_path,
        format="rdfxml"
    )

    print(
        "DAA ontology created successfully!"
    )