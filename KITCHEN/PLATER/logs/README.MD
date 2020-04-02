List of files in current dir:
- edge_errors.json: contains summary of kgx edge validation
- node_errors.json: contains summary of kgx node validation
- graph_summary.json: contains summary of the graph. 
  To reset just delete this file or run PLATER 
  with -rs (--reset-summary) cli argument .
- graph_diff.json: is created after a second run of PLATER.
It is created using graph_summary.json as reference. 
  It will summarize out differences in stats of the graph.
- plater.log: log file of the application