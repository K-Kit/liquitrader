

class Condition:
    """
    Base class condition:
    Holds a dict of pairs, along with their floor/ceiling depending on condition type
    """

    def __init__(self):
        self.pairs_trailing = {}

    def evaluate(self, pair):
        """
        evaluate single pair against conditions
        if not in pairs_trailing and conditions = true : add to dict, set floor/ceiling at price -> return true
        else if conditions = false : remove from pairs_trailing -> return False
        else if in pairs_trailing and conditions = true and trail > trailing value: return amount to buy/sell
        :param pair:
        :return:
        """
        pass

    def update_trail_data(self, pairs):
        """
        Update pairs_trailing dict information:
        for buy condition 'if price < floor then floor = price'
        same idea with ceiling for sales
        :return: dict
        """
        pass