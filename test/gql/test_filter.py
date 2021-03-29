import unittest
from weaviate.gql.filter import NearText, NearVector, NearObject, WhereFilter
from test.util import check_error_message, check_startswith_error_message


def helper_get_test_filter(type, value):
    return {
        "path": ["name"],
        "operator": "Equal",
        type: value
    }


class TestNearText(unittest.TestCase):

    def move_x_test_case(self, move: str):
        """
        Test the "moveTo" or the "moveAwayFrom" clause.

        Parameters
        ----------
        move : str
            The "moveTo" or the "moveAwayFrom" clause name.
        """

        type_error_message = f"`move` clause should be dict but was {str}"
        concepts_objects_error_message = "The 'move' clause should contain `concepts` OR/AND `objects`!"
        objects_type_error_message = lambda dt: f"'objects' must be of type list or dict, not {dt}"
        object_value_error_message = 'Each object from the `move` clause should have ONLY `id` OR `beacon`!'
        concept_value_error_message = f"Concepts must be of type list or str, not {set}"
        force_error_message = "'move' clause needs to state a 'force'"
        force_type_error_message = f"'force' should be float but was {bool}"

        with self.assertRaises(TypeError) as error:
            NearText({
                "concepts": "Some_concept",
                move: "0.5"
            })
        check_error_message(self, error, type_error_message)

        with self.assertRaises(ValueError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {}
            })
        check_error_message(self, error, concepts_objects_error_message)

        with self.assertRaises(TypeError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {
                    "concepts" : set("something")
                }
            })
        check_error_message(self, error, concept_value_error_message)

        with self.assertRaises(ValueError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {
                    "concepts" : "something",
                }
            })
        check_error_message(self, error, force_error_message)

        with self.assertRaises(TypeError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {
                    "objects" : 1234,
                }
            })
        check_error_message(self, error, objects_type_error_message(int))

        with self.assertRaises(ValueError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {
                    "objects" : {},
                }
            })
        check_error_message(self, error, object_value_error_message)

        with self.assertRaises(ValueError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {
                    "objects" : {'id': 1, 'beacon': 2},
                }
            })
        check_error_message(self, error, object_value_error_message)

        with self.assertRaises(ValueError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {
                    "objects" : {'test_id': 1},
                }
            })
        check_error_message(self, error, object_value_error_message)

        with self.assertRaises(TypeError) as error:
            NearText({
                "concepts": "Some_concept",
                move: {
                    "concepts": "something",
                    "objects" : [{'id': 1}],
                    "force": True
                }
            })
        check_error_message(self, error, force_type_error_message)

    def test___init__(self):
        """
        Test the `__init__` method.
        """

        # invalid calls
        content_error_message = f"NearText filter is expected to be type dict but was {list}"
        concept_error_message = "No concepts in content"
        concept_value_error_message = f"Concepts must be of type list or str, not {set}"
        certainty_error_message = ("certainty is expected to be a float but was "
                    f"{str}")
        ## test "concepts"
        with self.assertRaises(TypeError) as error:
            NearText(["concepts", "Some_concept"])
        check_error_message(self, error, content_error_message)

        with self.assertRaises(ValueError) as error:
            NearText({"INVALID": "Some_concept"})
        check_error_message(self, error, concept_error_message)

        with self.assertRaises(TypeError) as error:
            NearText({"concepts" : set("Some_concept")})
        check_error_message(self, error, concept_value_error_message)

        ## test "certainty"
        with self.assertRaises(TypeError) as error:
            NearText({
                "concepts": "Some_concept",
                "certainty": "0.5"
            })
        check_error_message(self, error, certainty_error_message)

        ## test "moveTo"
        self.move_x_test_case("moveTo")
        ## test "moveAwayFrom"
        self.move_x_test_case("moveAwayFrom")

        # test valid calls
        NearText(
            {
                "concepts": "Some_concept"
            }
        )
        NearText(
            {
                "concepts": ["Some_concept", "Some_concept_2"]
            }
        )
        NearText(
            {
                "concepts": "Some_concept",
                "certainty": 0.75
            }
        )
        NearText(
            {
                "concepts": "Some_concept",
                "moveTo": {
                    "concepts": "moveToConcepts",
                    "force": 0.75
                }
            }
        )
        NearText(
            {
                "concepts": "Some_concept",
                "moveAwayFrom": {
                    "concepts": "moveAwayFromConcepts",
                    "force": 0.75
                }
            }
        )
        NearText(
            {
                "concepts": "Some_concept",
                "certainty": 0.75,
                "moveAwayFrom": {
                    "concepts": "moveAwayFromConcepts",
                    "force": 0.75
                },
                "moveTo": {
                    "concepts": "moveToConcepts",
                    "force": 0.75
                }
            }
        )

        NearText(
            {
                "concepts": "Some_concept",
                "certainty": 0.75,
                "moveAwayFrom": {
                    "objects": {'id': "test_id"},
                    "force": 0.75
                },
                "moveTo": {
                    "concepts": "moveToConcepts",
                    "objects": [{'id': "test_id"}, {'beacon': 'Test_beacon'}],
                    "force": 0.75
                }
            }
        )

    def test___str__(self):
        """
        Test the `__str__` method.
        """
        
        near_text = NearText(
            {
                "concepts": "Some_concept"
            }
        )
        self.assertEqual(str(near_text), 'nearText: {concepts: ["Some_concept"]} ')

        near_text = NearText(
            {
                "concepts": ["Some_concept", "Some_concept_2"]
            }
        )
        self.assertEqual(str(near_text), 'nearText: {concepts: ["Some_concept", "Some_concept_2"]} ')
        near_text = NearText(
            {
                "concepts": "Some_concept",
                "certainty": 0.75
            }
        )
        self.assertEqual(str(near_text), 'nearText: {concepts: ["Some_concept"] certainty: 0.75} ')
        near_text = NearText(
            {
                "concepts": "Some_concept",
                "moveTo": {
                    "concepts": "moveToConcepts",
                    "force": 0.75
                }
            }
        )
        self.assertEqual(str(near_text), 'nearText: {concepts: ["Some_concept"] moveTo: {concepts: ["moveToConcepts"] force: 0.75}} ')
        near_text = NearText(
            {
                "concepts": "Some_concept",
                "moveAwayFrom": {
                    "concepts": "moveAwayFromConcepts",
                    "force": 0.25
                }
            }
        )
        self.assertEqual(str(near_text), 'nearText: {concepts: ["Some_concept"] moveAwayFrom: {concepts: ["moveAwayFromConcepts"] force: 0.25}} ')
        near_text = NearText(
            {
                "concepts": "Some_concept",
                "certainty": 0.95,
                "moveAwayFrom": {
                    "concepts": "moveAwayFromConcepts",
                    "force": 0.75
                },
                "moveTo": {
                    "concepts": "moveToConcepts",
                    "force": 0.25
                }
            }
        )
        self.assertEqual(str(near_text), 'nearText: {concepts: ["Some_concept"] certainty: 0.95 moveTo: {concepts: ["moveToConcepts"] force: 0.25} moveAwayFrom: {concepts: ["moveAwayFromConcepts"] force: 0.75}} ')

        # test it with references of objects
        concepts = ["con1", "con2"]
        move = {
            "concepts": "moveToConcepts",
            "force": 0.75
        }

        near_text = NearText(
            {
                "concepts": concepts,
                "moveTo": move
            }
        )
        concepts.append("con3") # should not be appended to the nearText clause
        move["force"] = 2.00 # should not be appended to the nearText clause
        self.assertEqual(str(near_text), 'nearText: {concepts: ["con1", "con2"] moveTo: {concepts: ["moveToConcepts"] force: 0.75}} ')


class TestNearVector(unittest.TestCase):

    def test___init__(self):
        """
        Test the `__init__` method.
        """

        # test exceptions
        content_error_message = ("NearVector filter is expected to "
                f"be type dict but was {list}")
        vector_error_message = "No 'vector' key in `content` argument."
        vector_value_error_message = f"'vector' key is expected to be type `list` but was {set}"
        certainty_error_message = ("certainty is expected to be a float but was "
                    f"{str}")

        ## test "concepts"
        with self.assertRaises(TypeError) as error:
            NearVector(["concepts", "Some_concept"])
        check_error_message(self, error, content_error_message)

        with self.assertRaises(ValueError) as error:
            NearVector({"INVALID": "Some_concept"})
        check_error_message(self, error, vector_error_message)

        with self.assertRaises(TypeError) as error:
            NearVector({"vector" : set("Some_concept")})
        check_error_message(self, error, vector_value_error_message)

        ## test "certainty"
        with self.assertRaises(TypeError) as error:
            NearVector({
                "vector": [1., 2., 3., 4.],
                "certainty": "0.5"
            })
        check_error_message(self, error, certainty_error_message)

        # test valid calls
        NearVector(
            {
                "vector": [1., 2., 3., 4.]
            }
        )
        NearVector(
            {
                "vector": [1., 2., 3., 4.],
                "certainty": 0.75
            }
        )

    def test___str__(self):
        """
        Test the `__str__` method.
        """
        
        near_vector = NearVector(
            {
                "vector": [1., 2., 3., 4.]
            }
        )
        self.assertEqual(str(near_vector), 'nearVector: {vector: [1.0, 2.0, 3.0, 4.0]} ')
        near_vector = NearVector(
            {
                "vector": [1., 2., 3., 4.],
                "certainty": 0.75
            }
        )
        self.assertEqual(str(near_vector), 'nearVector: {vector: [1.0, 2.0, 3.0, 4.0] certainty: 0.75} ')


class TestNearObject(unittest.TestCase):

    def test___init__(self):
        """
        Test the `__init__` method.
        """

        # invalid calls

        ## error messages 
        content_error_message = lambda dt: f"NearObject filter is expected to be type dict but was {dt}"
        beacon_id_error_message = "The 'content' argument should contain EITHER `id` OR `beacon`!"
        beacon_id_type_error_message = lambda dt: ("The 'id'/'beacon' should be of type string! Given type" + str(dt))
        certainty_error_message = lambda dt: f"certainty is expected to be a float but was {dt}"

        with self.assertRaises(TypeError) as error:
            NearObject(123)
        check_error_message(self, error, content_error_message(int))

        with self.assertRaises(ValueError) as error:
            NearObject({
                'id': 123,
                'beacon': 456
            })
        check_error_message(self, error, beacon_id_error_message)

        with self.assertRaises(TypeError) as error:
            NearObject({
                'id': 123,
            })
        check_error_message(self, error, beacon_id_type_error_message(int))

        with self.assertRaises(TypeError) as error:
            NearObject({
                'beacon': {123},
            })
        check_error_message(self, error, beacon_id_type_error_message(set))

        with self.assertRaises(TypeError) as error:
            NearObject({
                'beacon': 'test_beacon',
                'certainty': False
            })
        check_error_message(self, error, certainty_error_message(bool))

        # valid calls

        NearObject({
            'id': 'test_id',
        })

        NearObject({
            'beacon': 'test_beacon',
            'certainty': 0.7
        })

    def test___str__(self):
        """
        Test the `__str__` method.
        """

        near_object = NearObject({
            'id': 'test_id',
        })
        self.assertEqual(str(near_object), 'nearObject: {id: test_id} ')

        near_object = NearObject({
            'id': 'test_id',
            'certainty': 0.7
        })
        self.assertEqual(str(near_object), 'nearObject: {id: test_id certainty: 0.7} ')

        near_object = NearObject({
            'beacon': 'test_beacon',
        })
        self.assertEqual(str(near_object), 'nearObject: {beacon: test_beacon} ')

        near_object = NearObject({
            'beacon': 'test_beacon',
            'certainty': 0.0
        })
        self.assertEqual(str(near_object), 'nearObject: {beacon: test_beacon certainty: 0.0} ')


class TestWhereFilter(unittest.TestCase):

    def test___init__(self):
        """
        Test the `__init__` method.
        """

        # test exceptions
        content_error_message = lambda dt: f"WhereFilter is expected to be type dict but was {dt}"
        content_key_error_message = "Filter is missing required fileds `path` or `operands`. Given: "
        path_key_error = "Filter is missing required filed `operator`. Given: "
        dtype_error_message = "Filter is missing required fileds: "

        with self.assertRaises(TypeError) as error:
            WhereFilter(None)
        check_error_message(self, error, content_error_message(type(None)))

        with self.assertRaises(TypeError) as error:
            WhereFilter("filter")
        check_error_message(self, error, content_error_message(str))

        with self.assertRaises(ValueError) as error:
            WhereFilter({})
        check_startswith_error_message(self, error, content_key_error_message)

        with self.assertRaises(ValueError) as error:
            WhereFilter({"path": "some_path"})
        check_startswith_error_message(self, error, path_key_error)

        with self.assertRaises(ValueError) as error:
            WhereFilter({"path": "some_path", "operator": "Like"})
        check_startswith_error_message(self, error, dtype_error_message)

        with self.assertRaises(ValueError) as error:
            WhereFilter({"operands": "some_path"})
        check_startswith_error_message(self, error, path_key_error)

        with self.assertRaises(TypeError) as error:
            WhereFilter({"operands": "some_path", "operator": "Like"})
        check_error_message(self, error, content_error_message(str))

        with self.assertRaises(TypeError) as error:
            WhereFilter({"operands": ["some_path"], "operator": "Like"})
        check_error_message(self, error, content_error_message(str))

        
        # test valid calls
        WhereFilter(
            {
                "path": "hasTheOneRing",
                "operator" : "Equal",
                "valueBoolean" : False
            }
        )
        WhereFilter(
            {
                "operands": [{
                    "path": "hasTheOneRing",
                    "operator" : "Equal",
                    "valueBoolean" : False
                },
                {
                    "path": "hasFriend",
                    "operator" : "Equal",
                    "valueText" : "Samwise Gamgee"
                }],
                "operator" : "And"
            }
        )

    def test___str__(self):
        """
        Test the `__str__` method.
        """

        test_filter = {
            "path": ["name"],
            "operator": "Equal",
            "valueString": "A"
        }
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueString: "A"} ', result)

        test_filter = {
            "operator": "Or",
            "operands": [{
                "path": ["name"],
                "operator": "Equal",
                "valueString": "Alan Truing"
            },
                {
                    "path": ["name"],
                    "operator": "Equal",
                    "valueString": "John von Neumann"
                }
            ]
        }
        result = str(WhereFilter(test_filter))
        self.assertEqual(
            'where: {operator: Or operands: [{path: ["name"] operator: Equal valueString: "Alan Truing"}, {path: ["name"] operator: Equal valueString: "John von Neumann"}]} ',
            result
        )

        # test dataTypes
        test_filter = helper_get_test_filter("valueText", "Test")
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueText: "Test"} ', result)

        test_filter = helper_get_test_filter("valueString", "Test")
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueString: "Test"} ', result)

        test_filter = helper_get_test_filter("valueInt", 1)
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueInt: 1} ', result)

        test_filter = helper_get_test_filter("valueNumber", 1.4)
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueNumber: 1.4} ', result)

        test_filter = helper_get_test_filter("valueBoolean", True)
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueBoolean: true} ', result)

        test_filter = helper_get_test_filter("valueDate", "test-2021-02-02")
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueDate: "test-2021-02-02"} ', result)

        geo_range = {
            "geoCoordinates": {
                "latitude": 51.51,
                "longitude": -0.09
            },
            "distance": {
                "max": 2000
            }
        }
        test_filter = helper_get_test_filter("valueGeoRange", geo_range)
        result = str(WhereFilter(test_filter))
        self.assertEqual('where: {path: ["name"] operator: Equal valueGeoRange: {"geoCoordinates": {"latitude": 51.51, "longitude": -0.09}, "distance": {"max": 2000}}} ', str(result))