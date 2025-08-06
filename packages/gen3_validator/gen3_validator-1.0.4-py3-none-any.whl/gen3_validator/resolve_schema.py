import json
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class ResolveSchema:
    def __init__(self, schema_path: str):
        """
        Initialize the ResolveSchema class.

        Parameters:
        - schema_path (str): The path to the JSON schema file.
        """
        self.schema_path = schema_path
        logger.info(f"Initializing ResolveSchema with schema path: {schema_path}")
        self.schema = None
        self.nodes = None
        self.node_pairs = None
        self.node_order = None
        self.schema_list = None
        self.schema_def = None
        self.schema_term = None
        self.schema_def_resolved = None
        self.schema_list_resolved = None
        self.schema_resolved = None
        self.schema_version = None

    def read_json(self, path: str) -> dict:
        """
        Read a JSON file and return its contents as a dictionary.

        Parameters:
        - path (str): The path to the JSON file.

        Returns:
        - dict: The contents of the JSON file.
        """
        logger.info(f"Reading JSON file from path: {path}")
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"JSON file not found: {path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from file {path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading JSON file {path}: {e}")
            raise

    def get_nodes(self) -> list:
        """
        Retrieve all node names from the schema.

        Returns:
        - list: A list of node names.
        """
        logger.info("Retrieving node names from schema.")
        try:
            nodes = list(self.schema.keys())
            return nodes
        except Exception as e:
            logger.error(f"Error retrieving nodes from schema: {e}")
            raise

    def get_node_link(self, node_name: str) -> tuple:
        """
        Retrieve the links and ID for a given node.

        Parameters:
        - node_name (str): The name of the node.

        Returns:
        - tuple: A tuple containing the node ID and its links.
        """
        logger.info(f"Retrieving links and ID for node: {node_name}")
        try:
            links = self.schema[node_name]["links"]
            node_id = self.schema[node_name]["id"]
            if "subgroup" in links[0]:
                return node_id, links[0]["subgroup"]
            else:
                return node_id, links
        except KeyError as e:
            logger.error(f"Missing key {e} in node {node_name}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving node link for {node_name}: {e}")
            raise

    def get_node_category(self, node_name: str) -> tuple:
        """
        Retrieve the category and ID for a given node, excluding certain nodes.

        Parameters:
        - node_name (str): The name of the node.

        Returns:
        - tuple: A tuple containing the node ID and its category, or None if the node is excluded.
        """
        logger.info(f"Retrieving category and ID for node: {node_name}")
        try:
            category = self.schema[node_name]["category"]
            node_id = self.schema[node_name]["id"]
            return node_id, category
        except KeyError as e:
            logger.error(f"Missing key {e} in node {node_name}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving node category for {node_name}: {e}")
            raise

    def get_node_properties(self, node_name: str) -> tuple:
        """
        Retrieve the properties for a given node.

        Parameters:
        - node_name (str): The name of the node.

        Returns:
        - tuple: A tuple containing the node ID and its properties.
        """
        logger.info(f"Retrieving properties for node: {node_name}")
        try:
            properties = {
                k: v for k, v in self.schema[node_name]["properties"].items()
                if k != "$ref"
            }
            property_keys = list(properties.keys())
            node_id = self.schema[node_name]["id"]
            return node_id, property_keys
        except KeyError as e:
            logger.error(f"Missing key {e} in node {node_name}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving node properties for {node_name}: {e}")
            raise

    def generate_node_lookup(self) -> dict:
        logger.info("Generating node lookup dictionary.")
        node_lookup = {}
        excluded_nodes = [
            "_definitions.yaml",
            "_terms.yaml",
            "_settings.yaml",
            "program.yaml",
        ]

        for node in self.nodes:
            if node in excluded_nodes:
                continue

            try:
                category = self.get_node_category(node)
                if category:
                    category = category[1]

                props = self.get_node_properties(node)
                node_lookup[node] = {"category": category, "properties": props}
            except Exception as e:
                logger.error(f"Error generating node lookup for {node}: {e}")
                continue
        return node_lookup

    def find_upstream_downstream(self, node_name: str) -> list:
        """
        Takes a node name and returns the upstream and downstream nodes.

        Parameters:
        - node_name (str): The name of the node.

        Returns:
        - list: A list of tuples representing upstream and downstream nodes.
        """
        logger.info(f"Finding upstream and downstream nodes for: {node_name}")
        try:
            node_id, links = self.get_node_link(node_name)

            # Ensure links is a list
            if isinstance(links, dict):
                links = [links]

            results = []

            for link in links:
                target_type = link.get("target_type")

                if not node_id or not target_type:
                    logger.warning(f"Missing essential keys in link: {link}")
                    results.append((None, None))
                    continue

                results.append((target_type, node_id))

            return results
        except Exception as e:
            logger.error(f"Error finding upstream/downstream for {node_name}: {e}")
            raise

    def get_all_node_pairs(
        self,
        excluded_nodes=[
            "_definitions.yaml",
            "_terms.yaml",
            "_settings.yaml",
            "program.yaml",
        ],
    ) -> list:
        """
        Retrieve all node pairs, excluding specified nodes.

        Parameters:
        - excluded_nodes (list): A list of node names to exclude.

        Returns:
        - list: A list of node pairs.
        """
        logger.info("Retrieving all node pairs, excluding specified nodes.")
        node_pairs = []
        for node in self.nodes:
            if node not in excluded_nodes:
                try:
                    node_pairs.extend(self.find_upstream_downstream(node))
                except Exception as e:
                    logger.error(f"Error retrieving node pairs for {node}: {e}")
                    continue
        return node_pairs

    def get_node_order(self, edges: list) -> list:
        """
        Determine the order of nodes based on their dependencies.

        Parameters:
        - edges (list): A list of tuples representing node dependencies.

        Returns:
        - list: A list of nodes in topological order.
        """
        logger.info("Determining node order based on dependencies.")
        try:
            # Build graph representation
            graph = defaultdict(list)
            in_degree = defaultdict(int)

            for upstream, downstream in edges:
                graph[upstream].append(downstream)
                in_degree[downstream] += 1
                if upstream not in in_degree:
                    in_degree[upstream] = 0

            # Perform Topological Sorting (Kahn's Algorithm)
            sorted_order = []
            zero_in_degree = deque([node for node in in_degree if in_degree[node] == 0])

            while zero_in_degree:
                node = zero_in_degree.popleft()
                sorted_order.append(node)

                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        zero_in_degree.append(neighbor)

            # Ensure core_metadata_collection is last
            if "core_metadata_collection" in sorted_order:
                sorted_order.remove("core_metadata_collection")
                sorted_order.append("core_metadata_collection")

            return sorted_order
        except Exception as e:
            logger.error(f"Error determining node order: {e}")
            raise

    def split_json(self) -> list:
        """
        Split the schema into a list of individual node schemas.

        Returns:
        - list: A list of node schemas.
        """
        logger.info("Splitting schema into individual node schemas.")
        try:
            schema_list = []
            for node in self.nodes:
                schema_list.append(self.schema[node])
            return schema_list
        except Exception as e:
            logger.error(f"Error splitting JSON schema: {e}")
            raise

    def return_schema(self, target_id: str) -> dict:
        """
        Retrieves the first dictionary from a list where the 'id' key matches the target_id.

        Parameters:
        - target_id (str): The value of the 'id' key to match.

        Returns:
        - dict: The dictionary that matches the target_id, or None if not found.
        """
        logger.info(f"Retrieving schema for target ID: {target_id}")
        try:
            if target_id.endswith(".yaml"):
                target_id = target_id[:-5]

            result = next(
                (item for item in self.schema_list if item.get("id") == target_id), None
            )
            if result is None:
                logger.warning(f"{target_id} not found in schema list")
            return result
        except Exception as e:
            logger.error(f"Error retrieving schema for {target_id}: {e}")
            raise

    def resolve_references(self, schema: dict, reference: dict) -> dict:
        """
        Takes a gen3 jsonschema draft 4 as a dictionary and recursively
        resolves any references using a reference schema which has no
        references.

        Parameters:
        - schema (dict): The JSON node to resolve references in.
        - reference (dict): The schema containing the references.

        Returns:
        - dict: The resolved JSON node with references resolved.
        """
        logger.info("Resolving references in schema.")
        ref_input_content = reference

        def resolve_node(node, manual_ref_content=ref_input_content):
            try:
                if isinstance(node, dict):
                    if "$ref" in node:
                        ref_path = node["$ref"]
                        ref_file, ref_key = ref_path.split("#")
                        ref_file = ref_file.strip()
                        ref_key = ref_key.strip("/")

                        # if a reference file is in the reference, load the pre-defined reference, if no file exists, then use the schema itself as reference
                        if ref_file:
                            ref_content = manual_ref_content
                        else:
                            ref_content = schema

                        for part in ref_key.split("/"):
                            ref_content = ref_content[part]

                        resolved_content = resolve_node(ref_content)
                        # Merge resolved content with the current node, excluding the $ref key
                        return {
                            **resolved_content,
                            **{k: resolve_node(v) for k, v in node.items() if k != "$ref"},
                        }
                    else:
                        return {k: resolve_node(v) for k, v in node.items()}
                elif isinstance(node, list):
                    return [resolve_node(item) for item in node]
                else:
                    return node
            except KeyError as e:
                logger.error(f"Missing key {e} while resolving references in node: {node}")
                raise
            except Exception as e:
                logger.error(f"Error resolving references in node: {e}")
                raise

        return resolve_node(schema)

    def schema_list_to_json(self, schema_list: list) -> dict:
        """
        Converts a list of JSON schemas to a dictionary where each key is the schema id
        with '.yaml' appended, and the value is the schema content.

        Parameters:
        - schema_list (list): A list of JSON schemas.

        Returns:
        - dict: A dictionary with schema ids as keys and schema contents as values.
        """
        logger.info("Converting schema list to JSON format.")
        try:
            schema_dict = {}
            for schema in schema_list:
                schema_id = schema.get("id")
                if schema_id:
                    schema_dict[f"{schema_id}.yaml"] = schema
            return schema_dict
        except Exception as e:
            logger.error(f"Error converting schema list to JSON: {e}")
            raise

    def resolve_all_references(self) -> list:
        """
        Resolves references in all other schema dictionaries using the resolved definitions schema.

        Returns:
        - list: A list of resolved schema dictionaries.
        """
        logger.info("Resolving all references in schema list.")
        logger.info("=== Resolving Schema References ===")

        resolved_schema_list = []
        for node in self.nodes:
            if node == "_definitions.yaml" or node == "_terms.yaml":
                continue

            try:
                resolved_schema = self.resolve_references(
                    self.schema[node], self.schema_def_resolved
                )
                resolved_schema_list.append(resolved_schema)
                logger.info(f"Resolved {node}")
            except KeyError as e:
                logger.error(f"Error resolving {node}: Missing key {e}")
            except Exception as e:
                logger.error(f"Error resolving {node}: {e}")

        return resolved_schema_list

    def return_resolved_schema(self, target_id: str) -> dict:
        """
        Retrieves the first dictionary from a list where the 'id' key matches the target_id.

        Parameters:
        - target_id (str): The value of the 'id' key to match.

        Returns:
        - dict: The dictionary that matches the target_id, or None if not found.
        """
        logger.info(f"Retrieving resolved schema for target ID: {target_id}")
        try:
            if target_id.endswith(".yaml"):
                target_id = target_id[:-5]

            result = next(
                (item for item in self.schema_list_resolved if item.get("id") == target_id),
                None,
            )
            if result is None:
                logger.warning(f"{target_id} not found in resolved schema list")
            return result
        except Exception as e:
            logger.error(f"Error retrieving resolved schema for {target_id}: {e}")
            raise

    def get_schema_version(self, schema: dict) -> str:
        """
        Extracts the version of the schema from the provided schema dictionary.

        Parameters:
        - schema (dict): The schema dictionary from which to extract the version.

        Returns:
        - str: The version of the schema.
        """
        try:
            version = schema['_settings.yaml']['_dict_version']
            return version
        except Exception as e:
            logger.error(f"Could not pull schema version {e}")
            raise

    def resolve_schema(self):
        """
        Resolves and initializes all schema-related attributes for the instance.
        This method reads the schema, extracts nodes and their relationships,
        splits and resolves references, and sets the schema version.
        """
        logger.info("Starting schema resolution process.")
        # Step 1: Read the main schema JSON
        self.schema = self.read_json(self.schema_path)
        logger.info("Successfully read JSON schema.")

        # Step 2: Extract node information
        self.nodes = self.get_nodes()
        logger.info(f"Retrieved {len(self.nodes)} nodes from schema.")

        # Step 3: Get node pairs and order
        self.node_pairs = self.get_all_node_pairs()
        logger.info(f"Retrieved {len(self.node_pairs)} node pairs.")
        self.node_order = self.get_node_order(edges=self.node_pairs)
        logger.info("Determined node order based on dependencies.")

        # Step 4: Split schema into individual node schemas
        self.schema_list = self.split_json()
        logger.info("Split schema into individual node schemas.")

        # Step 5: Retrieve definitions and terms schemas
        self.schema_def = self.return_schema("_definitions.yaml")
        logger.info("Retrieved definitions schema.")
        self.schema_term = self.return_schema("_terms.yaml")
        logger.info("Retrieved terms schema.")

        # Step 6: Resolve references in definitions
        self.schema_def_resolved = self.resolve_references(
            self.schema_def, self.schema_term
        )
        logger.info("Resolved references in definitions schema.")

        # Step 7: Resolve all references in schema list
        self.schema_list_resolved = self.resolve_all_references()
        logger.info("Resolved all references in schema list.")

        # Step 8: Convert resolved schema list to JSON format
        self.schema_resolved = self.schema_list_to_json(self.schema_list_resolved)
        logger.info("Converted resolved schema list to JSON format.")

        # Step 9: Get schema version
        self.schema_version = self.get_schema_version(self.schema)
        logger.info(f"Obtained schema version: {self.schema_version}")