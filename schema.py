import graphene
from graphene import relay
import time
global lt
import json


class Pair(graphene.ObjectType):
    """A Pair in the Star Wars saga"""

    class Meta:
        interfaces = (relay.Node,)

    symbol = graphene.String(description="The Symbol of the Pair.")
    close = graphene.Float()
    total = graphene.Float()
    def resolve_price(self):
        return self.close
    percentage = graphene.Float()
    volume = graphene.Float()
    bought_value = graphene.Float()
    current_value = graphene.Float()
    dca_lvl = graphene.Int()
    amount = graphene.Float()

    @classmethod
    def get_node(cls, info, id):
        return lt.exchange.pairs[id]


class PairConnection(relay.Connection):
    class Meta:
        node = Pair

#
# class Faction(graphene.ObjectType):
#     """A faction in the Star Wars saga"""
#
#     class Meta:
#         interfaces = (relay.Node,)
#
#     name = graphene.String(description="The name of the faction.")
#     ships = relay.ConnectionField(
#         ShipConnection, description="The ships used by the faction."
#     )
#
#     def resolve_ships(self, info, **args):
#         # Transform the instance ship_ids into real instances
#         return [get_ship(ship_id) for ship_id in self.ships]
#
#     @classmethod
#     def get_node(cls, info, id):
#         return get_faction(id)
#
#
# class IntroduceShip(relay.ClientIDMutation):
#     class Input:
#         ship_name = graphene.String(required=True)
#         faction_id = graphene.String(required=True)
#
#     ship = graphene.Field(Ship)
#     faction = graphene.Field(Faction)
#
#     @classmethod
#     def mutate_and_get_payload(
#         cls, root, info, ship_name, faction_id, client_mutation_id=None
#     ):
#         ship = create_ship(ship_name, faction_id)
#         faction = get_faction(faction_id)
#         return IntroduceShip(ship=ship, faction=faction)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    pairs = graphene.List(Pair,
                            symbol=graphene.String(),
                            id=graphene.String(),
                            )



    def resolve_pairs(self, info):
        print(lt.exchange.pairs.items())
        return list(lt.exchange.pairs.values())




# class Mutation(graphene.ObjectType):
#     introduce_ship = IntroduceShip.Field()

if __name__ == '__main__':
    schema = graphene.Schema(query=Query)

    from liquitrader import main

    global lt
    lt = main()
    time.sleep(5)
    query = """
        query something{
          pair(id: "ADA/ETH") {
            id
          }
        }
    """

    from flask_graphql import GraphQLView
    from flask import Flask
    app = Flask(__name__)

    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

    # Optional, for adding batch query support (used in Apollo-Client)
    # app.add_url_rule('/graphql/batch', view_func=GraphQLView.as_view('graphql', schema=schema, batch=True))
    app.run(debug=True)