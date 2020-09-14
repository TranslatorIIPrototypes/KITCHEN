```python
import requests
```


```python
kp_url = "https://automat.renci.org/hmdb"
overlay_endpoint ="/overlay"
```
Overlay would link up nodes in node bindings of a result set.
So for simplicity of this example, we could send a result with two nodes.


```python
knowledge_graph = {
  "query_graph": {
    "nodes": [
      {
        "id": "n1",
        "type": "named_thing",
        "curie": "NCBIGene:93034"
      },
      {
        "id": "n2",
        "type": "named_thing"
      }
    ],
    "edges": [
      {
        "id": "e0",
        "source_id": "n1",
        "target_id": "n2"
      }
    ]
  },
  "knowledge_graph": {
    "nodes": [
    ],
    "edges": [
    ]
  },
  "results": [
    {
      "edge_bindings": [],
      "node_bindings": [
        {
          "kg_id": "NCBIGene:93034",
          "qg_id": "n1"
        },
        {
          "kg_id": "CHEBI:14648",
          "qg_id": "n2"
        }
      ]
    }
  ]
}
response = requests.post(kp_url + overlay_endpoint, json=knowledge_graph).json()
```

in the response if kp has found an edge for the sets of nodes in a node binding, it will add support edges in the edge binding of the same result. All support edges will have 's_' prefixed ids as the qg_id , and kg_id would be the id from db. 

Also the full edge info is added to `['knowledge_graph']['edges']`


```python
import json 
print(json.dumps(response, indent=2))
```

    {
      "query_graph": {
        "nodes": [
          {
            "id": "n1",
            "type": "named_thing",
            "curie": "NCBIGene:93034"
          },
          {
            "id": "n2",
            "type": "named_thing"
          }
        ],
        "edges": [
          {
            "id": "e0",
            "source_id": "n1",
            "target_id": "n2"
          }
        ]
      },
      "results": [
        {
          "edge_bindings": [
            {
              "qg_id": "s_0",
              "kg_id": "b80d66ececb90bc98aa0056045fae8b4"
            }
          ],
          "node_bindings": [
            {
              "kg_id": "NCBIGene:93034",
              "qg_id": "n1"
            },
            {
              "kg_id": "CHEBI:14648",
              "qg_id": "n2"
            }
          ]
        }
      ],
      "knowledge_graph": {
        "nodes": [],
        "edges": [
          {
            "predicate_id": "RO:0002434",
            "relation_label": "interacts with",
            "edge_source": "hmdb.enzyme_to_metabolite",
            "ctime": 1582216202.5186,
            "id": "b80d66ececb90bc98aa0056045fae8b4",
            "source_database": "hmdb",
            "relation": "RO:0002434",
            "publications": [],
            "source_id": "CHEBI:14648",
            "target_id": "NCBIGene:93034"
          }
        ]
      }
    }  
```
