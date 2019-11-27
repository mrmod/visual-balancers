import flask
from backend import LoadBalancerConfig, load_balancer_graph

api = flask.Flask(__name__)
model = LoadBalancerConfig()
# TODO: CORS

@api.route('/load_balancers', methods=['GET'])
def get_load_balancers():
    return flask.jsonify(model.get_load_balancers())

@api.route('/target_groups', methods=['GET', 'POST'])
def get_target_groups():
    if flask.request.method == 'GET':
        return flask.jsonify(model.get_target_groups())
    if flask.request.method == 'POST':
        try:
            return flask.jsonify(model.get_target_group_members(
                flask.request.get_json()['target_group_arn'],
            ))
        except KeyError:
            return 400, 'missing target group arn'
    return 400, 'unsupported'

@api.route('/security_groups', methods=['POST'])
def get_security_group():
    try:
        group_id = flask.request.get_json()['security_group_id']
    except KeyError:
        return 400, 'missing security group id'
    return flask.jsonify(model.get_security_group(group_id))

@api.route('/graph', methods=['GET'])
def get_graph():
    return flask.jsonify(load_balancer_graph())

if __name__ == '__main__':
    api.run()