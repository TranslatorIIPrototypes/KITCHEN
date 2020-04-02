import json
import os

from PLATER.services.config import config
from PLATER.services.util.logutil import LoggingUtil

logger = LoggingUtil.init_logging(__name__,
                                  config.get('logging_level'),
                                  config.get('logging_format')
                                  )


class BuildComparisionValidator:
    def __init__(self, graph_interface, reset_summary=False):
        logger.info('initializing build comparision validator')
        self.graph_interface = graph_interface
        self.graph_interface.get_schema()
        self.summary = self.graph_interface.summary
        self.reset_summary = reset_summary
        self.summary_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'graph_summary.json')
        # create new summary file if reset is set
        if reset_summary:
            self.write_summary_to_file()
        self.diff_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'graph_diff.json')

    def validate(self):
        """
        Compares graph summaries and returns true if no difference was detected.
        :return: bool. True if no difference.
        """
        previous_build_summary = self.get_previous_build_summary()
        if not previous_build_summary:
            logger.info('There is no build summary to compare to. Saving current summary.')
            self.write_summary_to_file()
            return True
        diff, not_diff = BuildComparisionValidator.get_diff(self.summary, previous_build_summary)
        if not not_diff:
            with open(self.diff_file, 'w') as diff_file:
                logger.info(f'writing build difference to {self.diff_file}.')
                json.dump(diff, diff_file, indent=2)
        return not_diff

    def write_summary_to_file(self):
        with open(self.summary_file, 'w') as s_f:
            json.dump(self.summary, s_f, indent=2)

    @staticmethod
    def get_diff(new, old):
        diff = {}
        valid = True
        # find none existing keys
        diff['types_in_previous_build_only'] = [node_type for node_type in old if node_type not in new]
        diff['types_in_current_build_only'] = [node_type for node_type in new if node_type not in old]
        disjoin = diff['types_in_previous_build_only'] + diff['types_in_current_build_only']
        if disjoin:
            valid = False
        for node_type in new:
            diff_per_node_type = {}
            if node_type in disjoin:
                continue
            old_target_set = old[node_type]
            new_target_set = new[node_type]
            # compare targets like before
            diff_per_node_type['target_nodes_in_previous_build_only'] = [node_type for node_type in old_target_set
                                                                         if node_type not in new_target_set]
            diff_per_node_type['target_nodes_in_current_build_only'] = [node_type for node_type in new_target_set
                                                                        if node_type not in old_target_set]
            per_type_disjoin = diff_per_node_type['target_nodes_in_previous_build_only'] + \
                               diff_per_node_type['target_nodes_in_current_build_only']
            # Compare edgesets
            if per_type_disjoin:
                valid = False
            for target_node_type in new_target_set:
                if target_node_type in per_type_disjoin or target_node_type == 'nodes_count':
                    continue
                # compare edges
                diff_per_edge_set = {
                    'edge_count_diff': []
                }
                new_build_edge_set = new_target_set[target_node_type]
                old_build_edge_set = old_target_set[target_node_type]
                edges_in_previous_build_only = [x for x in old_build_edge_set if x not in new_build_edge_set]
                edges_in_current_build_only = [x for x in new_build_edge_set if x not in old_build_edge_set]
                if edges_in_previous_build_only:
                    diff_per_edge_set['edges_in_previous_build_only'] = {
                        'description': f'from {node_type} --> {target_node_type}',
                        'edges': edges_in_previous_build_only
                    }
                if edges_in_current_build_only:
                    diff_per_edge_set['edges_in_current_build_only'] = {
                        'description': f'from {node_type} --> {target_node_type}',
                        'edges': edges_in_current_build_only
                    }
                edges_disjoin = edges_in_current_build_only + edges_in_previous_build_only
                if edges_disjoin:
                    valid = False
                diff_per_edge_set['edge_count_diff'] = []
                for edge, new_build_edge_count in new_build_edge_set.items():
                    if edge in edges_disjoin:
                        continue
                    edge_count_diff = old_build_edge_set[edge] - new_build_edge_count
                    diff_message = 'No edge diff'
                    if edge_count_diff > 0:
                        valid = False
                        diff_message = f'Old build had {abs(edge_count_diff)} more  `{edge}` edges. ' \
                            f'{node_type} --> {target_node_type}'
                    if edge_count_diff < 0:
                        valid = False
                        diff_message = f'New build has {abs(edge_count_diff)} more `{edge}` edges. ' \
                            f'{node_type} --> {target_node_type}'
                    diff_per_edge_set['edge_count_diff'] += [diff_message]

                diff_per_node_type[target_node_type] = diff_per_edge_set
            # add node type diff to main diff
            diff[node_type] = diff_per_node_type
        return diff, valid

    def get_previous_build_summary(self):
        if os.path.exists(self.summary_file):
            with open(self.summary_file) as summary_file:
                return json.load(summary_file)
        return None
