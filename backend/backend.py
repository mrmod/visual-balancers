
import boto3
import logging
import itertools
from typing import List, Dict, Optional

class Tree(object):
    def __init__(self):
        self.nodes = []

    def append(self, node):
        node.id = len(self.nodes)
        self.nodes.append(node)
    
    def d3_nodes(self) -> List:
        return [{'name': n.name} for n in self.nodes]

    def d3_links(self) -> List:
        _links = []
        for node in self.nodes:
            if node.parent_id is None:
                continue
            _links.append({
                'source': node.parent_id,
                'target': node.id,
                'value': self.get_child_cost(
                    node.parent_id,
                    self.get_cost(node.parent_id),
                )
            })
        return _links

    def get_children_of_parent(self, parent_id) -> List:
        return [node for node in self.nodes if node.parent_id == parent_id]

    def get_child_cost(self, parent_id, parent_cost: float) -> float:
        child_cost = parent_cost / len(self.get_children_of_parent(parent_id))
        if child_cost >= parent_cost:
            return parent_cost/2
        return child_cost

    def get_cost(self, id) -> float:
        return self.nodes[id].cost

    def d3_graph(self):
        return {
            'nodes': self.d3_nodes(),
            'links': self.d3_links(),
        }

class Node(object):
    def __init__(self, name:str, parent=None, cost=1):
      self.id = 0
      if parent is None:
          self.parent_id = None
      else:
          self.parent_id = parent.id
      self.name = name
      self.cost = cost
    def __repr__(self):
        return f'{self.id} Name: {self.name} Cost: {self.cost} Parent: {self.parent_id}'

class LoadBalancerConfig(object):
    def __init__(self):
        self.client = boto3.client('elbv2')
        self.ec2_client = boto3.client('ec2')
        self.target_groups = []
        self.target_group_members = {}
        self.load_balancers = []
    
    def get_load_balancers(self) -> List:
        """
        List all load balancers
        """
        try:
            self.load_balancers = self.client.describe_load_balancers()['LoadBalancers']
        except KeyError:
            logging.error('Unable to list load balancers')
        except Exception as e:
            logging.error(f'Unexpected error: {e}')
        return self.load_balancers
    
    def get_target_groups(self) -> List:
        """
        List all load balancer target groups
        """
        try:
            self.target_groups = self.client.describe_target_groups()['TargetGroups']
        except KeyError:
            logging.error('Unable to list target groups')
        except Exception as e:
            logging.error(f'Unexpected error: {e}')

        return self.target_groups

    def get_target_group_members(self, group_arn:str) -> Dict:
        """
        List all targets of a group
        Args:
            group_arn (str): Target group arn
        """
        if len(self.target_groups) == 0:
            _ = self.get_target_groups()
        try:
            result = self.client.describe_target_health(TargetGroupArn=group_arn)
            return result['TargetHealthDescriptions']
        except KeyError:
            logging.error(f'Unable to get targets for {group_arn}')
        except Exception as e:
            logging.error(f'Unexpected error {e}')
        return []
    
    def get_security_group(self, group_id:str) -> List:
        """
        Get a single security group
        Args:
            group_id(str): Security group ID
        """
        group_ids = [group_id]
        try:
            r = self.ec2_client.describe_security_groups(GroupIds=group_ids)
            return r['SecurityGroups'][0]
        except KeyError:
            logging.error(f'Unable to get security group {group_id}')
        except Exception as e:
            logging.error(f'Unexpected error {e}')
        return []

def load_balancer_graph():
    lb_config = LoadBalancerConfig()
    graph = Tree()
    root = Node('The internet')
    graph.append(root)
    lb_nodes = {}
    for lb in lb_config.get_load_balancers():
        # Attach a load balancer to a security group
        for group_id in lb['SecurityGroups']:
            name = f"SecurityGroup-{group_id}"
            sg_node = Node(name, parent=root)
            graph.append(sg_node)

            lb_node = Node(lb['LoadBalancerName'], parent=sg_node)
            graph.append(lb_node)
            lb_nodes[lb['LoadBalancerArn']] = lb_node

    tg_nodes = {}
    for tg in lb_config.get_target_groups():
        # Fill a target group with targets
        for arn in tg['LoadBalancerArns']:
            try:
                lb_node = lb_nodes[arn]
                tg_node = Node(tg['TargetGroupName'], parent=lb_node)
                tg_nodes[tg['TargetGroupArn']] = tg_node
                graph.append(tg_node)
            except KeyError:
                logging.warning(f'Unable to resolve LB ARN {arn} to a saved node')

    for arn, tg_node in tg_nodes.items():
        targets = lb_config.get_target_group_members(arn)
        for target in targets:
            target_name = f"{target['Target']['Id']}:{target['Target']['Port']}"
            target_node = Node(target_name, parent=tg_node)
            graph.append(target_node)
    return graph.d3_graph()


def name_tag(tags:List[Dict]) -> Optional[str]:
    for tag in tags:
        try: 
            if tag['Key'] == 'Name':
                return tag['Value']
        except KeyError:
            pass
    return None