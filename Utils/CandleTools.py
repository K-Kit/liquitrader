import pandas as pd


def candles_to_df(candle_list):
    candles = pd.DataFrame(candle_list, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return candles.set_index(pd.to_datetime(candles.timestamp.values, unit='ms').values)


def candle_tic_to_df(candle):
    # take in candlestick WebSocket tic data, return dataframe in form of candlestick dataframe to merge into main candle dframe
    #k = data['k']
    #candle = [k['t'], k['o'], k['h'], k['l'], k['c'], k['v']]
    df = pd.DataFrame(candle, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df.set_index(pd.to_datetime(df.timestamp.values, unit='ms').values)


if __name__ == '__main__':
    data = {'timestamp': {1535455200000.0: 1535455200000.0, 1535455500000.0: 1535455500000.0, 1535455800000.0: 1535455800000.0, 1535456100000.0: 1535456100000.0, 1535456400000.0: 1535456400000.0, 1535456700000.0: 1535456700000.0, 1535457000000.0: 1535457000000.0, 1535457300000.0: 1535457300000.0, 1535457600000.0: 1535457600000.0, 1535457900000.0: 1535457900000.0, 1535458200000.0: 1535458200000.0, 1535458500000.0: 1535458500000.0, 1535458800000.0: 1535458800000.0, 1535459100000.0: 1535459100000.0, 1535459400000.0: 1535459400000.0, 1535459700000.0: 1535459700000.0, 1535460000000.0: 1535460000000.0, 1535460300000.0: 1535460300000.0, 1535460600000.0: 1535460600000.0, 1535460900000.0: 1535460900000.0, 1535461200000.0: 1535461200000.0, 1535461500000.0: 1535461500000.0, 1535461800000.0: 1535461800000.0, 1535462100000.0: 1535462100000.0, 1535462400000.0: 1535462400000.0, 1535462700000.0: 1535462700000.0, 1535463000000.0: 1535463000000.0, 1535463300000.0: 1535463300000.0, 1535463600000.0: 1535463600000.0, 1535463900000.0: 1535463900000.0, 1535464200000.0: 1535464200000.0, 1535464500000.0: 1535464500000.0, 1535464800000.0: 1535464800000.0, 1535465100000.0: 1535465100000.0, 1535465400000.0: 1535465400000.0, 1535465700000.0: 1535465700000.0, 1535466000000.0: 1535466000000.0, 1535466300000.0: 1535466300000.0, 1535466600000.0: 1535466600000.0, 1535466900000.0: 1535466900000.0, 1535467200000.0: 1535467200000.0, 1535467500000.0: 1535467500000.0, 1535467800000.0: 1535467800000.0, 1535468100000.0: 1535468100000.0, 1535468400000.0: 1535468400000.0, 1535468700000.0: 1535468700000.0, 1535469000000.0: 1535469000000.0, 1535469300000.0: 1535469300000.0, 1535469600000.0: 1535469600000.0, 1535469900000.0: 1535469900000.0, 1535470200000.0: 1535470200000.0, 1535470500000.0: 1535470500000.0, 1535470800000.0: 1535470800000.0, 1535471100000.0: 1535471100000.0, 1535471400000.0: 1535471400000.0, 1535471700000.0: 1535471700000.0, 1535472000000.0: 1535472000000.0, 1535472300000.0: 1535472300000.0, 1535472600000.0: 1535472600000.0, 1535472900000.0: 1535472900000.0, 1535473200000.0: 1535473200000.0, 1535473500000.0: 1535473500000.0, 1535473800000.0: 1535473800000.0, 1535474100000.0: 1535474100000.0, 1535474400000.0: 1535474400000.0, 1535474700000.0: 1535474700000.0, 1535475000000.0: 1535475000000.0, 1535475300000.0: 1535475300000.0, 1535475600000.0: 1535475600000.0, 1535475900000.0: 1535475900000.0, 1535476200000.0: 1535476200000.0, 1535476500000.0: 1535476500000.0, 1535476800000.0: 1535476800000.0, 1535477100000.0: 1535477100000.0, 1535477400000.0: 1535477400000.0, 1535477700000.0: 1535477700000.0, 1535478000000.0: 1535478000000.0, 1535478300000.0: 1535478300000.0, 1535478600000.0: 1535478600000.0, 1535478900000.0: 1535478900000.0, 1535479200000.0: 1535479200000.0, 1535479500000.0: 1535479500000.0, 1535479800000.0: 1535479800000.0, 1535480100000.0: 1535480100000.0, 1535480400000.0: 1535480400000.0, 1535480700000.0: 1535480700000.0, 1535481000000.0: 1535481000000.0, 1535481300000.0: 1535481300000.0, 1535481600000.0: 1535481600000.0, 1535481900000.0: 1535481900000.0, 1535482200000.0: 1535482200000.0, 1535482500000.0: 1535482500000.0, 1535482800000.0: 1535482800000.0, 1535483100000.0: 1535483100000.0, 1535483400000.0: 1535483400000.0, 1535483700000.0: 1535483700000.0, 1535484000000.0: 1535484000000.0, 1535484300000.0: 1535484300000.0, 1535484600000.0: 1535484600000.0, 1535484900000.0: 1535484900000.0}, 'open': {1535455200000.0: 0.00035747, 1535455500000.0: 0.0003577, 1535455800000.0: 0.0003585, 1535456100000.0: 0.00035826, 1535456400000.0: 0.00035796, 1535456700000.0: 0.00035839, 1535457000000.0: 0.00035859, 1535457300000.0: 0.0003591, 1535457600000.0: 0.00035843, 1535457900000.0: 0.00035947, 1535458200000.0: 0.00035889, 1535458500000.0: 0.00035819, 1535458800000.0: 0.0003585, 1535459100000.0: 0.00035892, 1535459400000.0: 0.0003572, 1535459700000.0: 0.00035704, 1535460000000.0: 0.00035785, 1535460300000.0: 0.00035662, 1535460600000.0: 0.00035694, 1535460900000.0: 0.00035694, 1535461200000.0: 0.00035729, 1535461500000.0: 0.0003566, 1535461800000.0: 0.00035758, 1535462100000.0: 0.000358, 1535462400000.0: 0.00035861, 1535462700000.0: 0.00035926, 1535463000000.0: 0.00035726, 1535463300000.0: 0.00035828, 1535463600000.0: 0.000359, 1535463900000.0: 0.00036, 1535464200000.0: 0.00036165, 1535464500000.0: 0.00036301, 1535464800000.0: 0.00036377, 1535465100000.0: 0.00036091, 1535465400000.0: 0.00036139, 1535465700000.0: 0.00036051, 1535466000000.0: 0.00035751, 1535466300000.0: 0.00035808, 1535466600000.0: 0.0003578, 1535466900000.0: 0.000358, 1535467200000.0: 0.00035854, 1535467500000.0: 0.000359, 1535467800000.0: 0.00035685, 1535468100000.0: 0.00035648, 1535468400000.0: 0.00035691, 1535468700000.0: 0.00035738, 1535469000000.0: 0.00035772, 1535469300000.0: 0.00035746, 1535469600000.0: 0.00035608, 1535469900000.0: 0.000356, 1535470200000.0: 0.00035433, 1535470500000.0: 0.00035529, 1535470800000.0: 0.00035522, 1535471100000.0: 0.00035547, 1535471400000.0: 0.00035549, 1535471700000.0: 0.00035468, 1535472000000.0: 0.00035532, 1535472300000.0: 0.00035688, 1535472600000.0: 0.00035688, 1535472900000.0: 0.00035777, 1535473200000.0: 0.00035887, 1535473500000.0: 0.00035653, 1535473800000.0: 0.00035374, 1535474100000.0: 0.00035373, 1535474400000.0: 0.0003568, 1535474700000.0: 0.00035516, 1535475000000.0: 0.00035575, 1535475300000.0: 0.0003554, 1535475600000.0: 0.00035555, 1535475900000.0: 0.00035598, 1535476200000.0: 0.0003562, 1535476500000.0: 0.00035498, 1535476800000.0: 0.00035537, 1535477100000.0: 0.00035519, 1535477400000.0: 0.00035466, 1535477700000.0: 0.0003548, 1535478000000.0: 0.000356, 1535478300000.0: 0.00035449, 1535478600000.0: 0.00035373, 1535478900000.0: 0.0003543, 1535479200000.0: 0.00035483, 1535479500000.0: 0.00035538, 1535479800000.0: 0.00035543, 1535480100000.0: 0.00035408, 1535480400000.0: 0.00035599, 1535480700000.0: 0.000356, 1535481000000.0: 0.00035616, 1535481300000.0: 0.00035655, 1535481600000.0: 0.00035697, 1535481900000.0: 0.00035724, 1535482200000.0: 0.00035611, 1535482500000.0: 0.00035701, 1535482800000.0: 0.00035697, 1535483100000.0: 0.00035667, 1535483400000.0: 0.00035581, 1535483700000.0: 0.00035677, 1535484000000.0: 0.00035775, 1535484300000.0: 0.00035773, 1535484600000.0: 0.00035849, 1535484900000.0: 0.00036002}, 'high': {1535455200000.0: 0.00035806, 1535455500000.0: 0.0003585, 1535455800000.0: 0.00035876, 1535456100000.0: 0.00035842, 1535456400000.0: 0.00035884, 1535456700000.0: 0.00035896, 1535457000000.0: 0.00035958, 1535457300000.0: 0.0003591, 1535457600000.0: 0.00035952, 1535457900000.0: 0.00035951, 1535458200000.0: 0.00035889, 1535458500000.0: 0.00035885, 1535458800000.0: 0.00035902, 1535459100000.0: 0.00035958, 1535459400000.0: 0.00035791, 1535459700000.0: 0.00035867, 1535460000000.0: 0.00035785, 1535460300000.0: 0.00035866, 1535460600000.0: 0.00035749, 1535460900000.0: 0.00035749, 1535461200000.0: 0.0003575, 1535461500000.0: 0.00035759, 1535461800000.0: 0.00035864, 1535462100000.0: 0.00035855, 1535462400000.0: 0.00035928, 1535462700000.0: 0.00035926, 1535463000000.0: 0.00035914, 1535463300000.0: 0.00035912, 1535463600000.0: 0.00036, 1535463900000.0: 0.00036204, 1535464200000.0: 0.00036301, 1535464500000.0: 0.00036384, 1535464800000.0: 0.00036377, 1535465100000.0: 0.00036139, 1535465400000.0: 0.00036139, 1535465700000.0: 0.0003606, 1535466000000.0: 0.00035919, 1535466300000.0: 0.00035877, 1535466600000.0: 0.0003578, 1535466900000.0: 0.00035812, 1535467200000.0: 0.000359, 1535467500000.0: 0.000359, 1535467800000.0: 0.00035721, 1535468100000.0: 0.00035748, 1535468400000.0: 0.00035738, 1535468700000.0: 0.00035821, 1535469000000.0: 0.00035775, 1535469300000.0: 0.00035746, 1535469600000.0: 0.00035608, 1535469900000.0: 0.00035601, 1535470200000.0: 0.00035598, 1535470500000.0: 0.00035596, 1535470800000.0: 0.00035549, 1535471100000.0: 0.00035549, 1535471400000.0: 0.00035549, 1535471700000.0: 0.00035688, 1535472000000.0: 0.00035713, 1535472300000.0: 0.00035715, 1535472600000.0: 0.00035821, 1535472900000.0: 0.00035888, 1535473200000.0: 0.00035891, 1535473500000.0: 0.00035656, 1535473800000.0: 0.00035412, 1535474100000.0: 0.00035726, 1535474400000.0: 0.00035731, 1535474700000.0: 0.00035653, 1535475000000.0: 0.00035713, 1535475300000.0: 0.00035619, 1535475600000.0: 0.00035619, 1535475900000.0: 0.00035671, 1535476200000.0: 0.0003562, 1535476500000.0: 0.00035616, 1535476800000.0: 0.0003555, 1535477100000.0: 0.00035519, 1535477400000.0: 0.00035546, 1535477700000.0: 0.0003548, 1535478000000.0: 0.000356, 1535478300000.0: 0.0003545, 1535478600000.0: 0.00035504, 1535478900000.0: 0.00035636, 1535479200000.0: 0.00035574, 1535479500000.0: 0.00035543, 1535479800000.0: 0.00035543, 1535480100000.0: 0.00035599, 1535480400000.0: 0.0003562, 1535480700000.0: 0.00035655, 1535481000000.0: 0.00035655, 1535481300000.0: 0.00035711, 1535481600000.0: 0.00035732, 1535481900000.0: 0.00035725, 1535482200000.0: 0.00035788, 1535482500000.0: 0.00035701, 1535482800000.0: 0.00035718, 1535483100000.0: 0.00035667, 1535483400000.0: 0.00035798, 1535483700000.0: 0.00035782, 1535484000000.0: 0.00035779, 1535484300000.0: 0.0003585, 1535484600000.0: 0.00036035, 1535484900000.0: 0.00036045}, 'low': {1535455200000.0: 0.0003573, 1535455500000.0: 0.00035737, 1535455800000.0: 0.00035784, 1535456100000.0: 0.00035735, 1535456400000.0: 0.00035774, 1535456700000.0: 0.00035795, 1535457000000.0: 0.00035772, 1535457300000.0: 0.00035843, 1535457600000.0: 0.00035843, 1535457900000.0: 0.00035781, 1535458200000.0: 0.0003573, 1535458500000.0: 0.00035737, 1535458800000.0: 0.000358, 1535459100000.0: 0.0003572, 1535459400000.0: 0.000357, 1535459700000.0: 0.00035704, 1535460000000.0: 0.00035654, 1535460300000.0: 0.00035662, 1535460600000.0: 0.0003563, 1535460900000.0: 0.00035622, 1535461200000.0: 0.0003566, 1535461500000.0: 0.0003565, 1535461800000.0: 0.00035681, 1535462100000.0: 0.00035774, 1535462400000.0: 0.0003575, 1535462700000.0: 0.00035703, 1535463000000.0: 0.000357, 1535463300000.0: 0.00035724, 1535463600000.0: 0.00035868, 1535463900000.0: 0.00035936, 1535464200000.0: 0.00036078, 1535464500000.0: 0.00036229, 1535464800000.0: 0.00036064, 1535465100000.0: 0.00036067, 1535465400000.0: 0.00035969, 1535465700000.0: 0.00035754, 1535466000000.0: 0.000357, 1535466300000.0: 0.0003578, 1535466600000.0: 0.00035569, 1535466900000.0: 0.00035713, 1535467200000.0: 0.00035613, 1535467500000.0: 0.0003527, 1535467800000.0: 0.00035538, 1535468100000.0: 0.00035583, 1535468400000.0: 0.00035691, 1535468700000.0: 0.00035738, 1535469000000.0: 0.00035716, 1535469300000.0: 0.00035505, 1535469600000.0: 0.000355, 1535469900000.0: 0.00035422, 1535470200000.0: 0.0003542, 1535470500000.0: 0.00035495, 1535470800000.0: 0.00035472, 1535471100000.0: 0.0003548, 1535471400000.0: 0.0003543, 1535471700000.0: 0.0003543, 1535472000000.0: 0.00035445, 1535472300000.0: 0.00035642, 1535472600000.0: 0.00035688, 1535472900000.0: 0.00035776, 1535473200000.0: 0.00035653, 1535473500000.0: 0.00035301, 1535473800000.0: 0.00035302, 1535474100000.0: 0.00035373, 1535474400000.0: 0.00035462, 1535474700000.0: 0.00035444, 1535475000000.0: 0.00035551, 1535475300000.0: 0.00035513, 1535475600000.0: 0.0003553, 1535475900000.0: 0.00035597, 1535476200000.0: 0.00035498, 1535476500000.0: 0.00035498, 1535476800000.0: 0.00035498, 1535477100000.0: 0.00035466, 1535477400000.0: 0.00035451, 1535477700000.0: 0.00035451, 1535478000000.0: 0.00035449, 1535478300000.0: 0.00035383, 1535478600000.0: 0.00035248, 1535478900000.0: 0.0003543, 1535479200000.0: 0.00035451, 1535479500000.0: 0.00035451, 1535479800000.0: 0.00035408, 1535480100000.0: 0.00035408, 1535480400000.0: 0.00035599, 1535480700000.0: 0.000356, 1535481000000.0: 0.0003555, 1535481300000.0: 0.00035572, 1535481600000.0: 0.00035572, 1535481900000.0: 0.00035483, 1535482200000.0: 0.00035611, 1535482500000.0: 0.00035585, 1535482800000.0: 0.00035609, 1535483100000.0: 0.00035585, 1535483400000.0: 0.00035581, 1535483700000.0: 0.00035667, 1535484000000.0: 0.00035667, 1535484300000.0: 0.00035712, 1535484600000.0: 0.00035814, 1535484900000.0: 0.00035881}, 'close': {1535455200000.0: 0.00035805, 1535455500000.0: 0.0003585, 1535455800000.0: 0.00035876, 1535456100000.0: 0.00035774, 1535456400000.0: 0.00035831, 1535456700000.0: 0.00035896, 1535457000000.0: 0.0003591, 1535457300000.0: 0.00035843, 1535457600000.0: 0.00035852, 1535457900000.0: 0.00035801, 1535458200000.0: 0.0003573, 1535458500000.0: 0.00035885, 1535458800000.0: 0.00035872, 1535459100000.0: 0.0003572, 1535459400000.0: 0.000357, 1535459700000.0: 0.00035775, 1535460000000.0: 0.00035758, 1535460300000.0: 0.00035694, 1535460600000.0: 0.00035694, 1535460900000.0: 0.00035733, 1535461200000.0: 0.0003566, 1535461500000.0: 0.00035759, 1535461800000.0: 0.00035774, 1535462100000.0: 0.00035797, 1535462400000.0: 0.00035915, 1535462700000.0: 0.00035747, 1535463000000.0: 0.0003579, 1535463300000.0: 0.00035838, 1535463600000.0: 0.00036, 1535463900000.0: 0.00036165, 1535464200000.0: 0.00036301, 1535464500000.0: 0.00036311, 1535464800000.0: 0.00036086, 1535465100000.0: 0.00036072, 1535465400000.0: 0.00035969, 1535465700000.0: 0.00035754, 1535466000000.0: 0.00035808, 1535466300000.0: 0.0003578, 1535466600000.0: 0.00035724, 1535466900000.0: 0.00035725, 1535467200000.0: 0.000359, 1535467500000.0: 0.00035605, 1535467800000.0: 0.00035648, 1535468100000.0: 0.00035748, 1535468400000.0: 0.00035738, 1535468700000.0: 0.00035772, 1535469000000.0: 0.00035746, 1535469300000.0: 0.00035611, 1535469600000.0: 0.00035551, 1535469900000.0: 0.00035536, 1535470200000.0: 0.00035598, 1535470500000.0: 0.00035581, 1535470800000.0: 0.00035549, 1535471100000.0: 0.00035549, 1535471400000.0: 0.00035468, 1535471700000.0: 0.00035515, 1535472000000.0: 0.00035601, 1535472300000.0: 0.00035715, 1535472600000.0: 0.00035776, 1535472900000.0: 0.00035887, 1535473200000.0: 0.00035653, 1535473500000.0: 0.00035302, 1535473800000.0: 0.00035412, 1535474100000.0: 0.00035676, 1535474400000.0: 0.00035496, 1535474700000.0: 0.00035575, 1535475000000.0: 0.00035551, 1535475300000.0: 0.00035619, 1535475600000.0: 0.00035619, 1535475900000.0: 0.0003562, 1535476200000.0: 0.00035498, 1535476500000.0: 0.00035509, 1535476800000.0: 0.00035506, 1535477100000.0: 0.00035466, 1535477400000.0: 0.0003548, 1535477700000.0: 0.00035451, 1535478000000.0: 0.00035449, 1535478300000.0: 0.00035383, 1535478600000.0: 0.000355, 1535478900000.0: 0.00035452, 1535479200000.0: 0.00035451, 1535479500000.0: 0.00035543, 1535479800000.0: 0.00035408, 1535480100000.0: 0.00035543, 1535480400000.0: 0.00035616, 1535480700000.0: 0.0003564, 1535481000000.0: 0.00035655, 1535481300000.0: 0.00035711, 1535481600000.0: 0.00035697, 1535481900000.0: 0.0003563, 1535482200000.0: 0.00035637, 1535482500000.0: 0.00035696, 1535482800000.0: 0.00035667, 1535483100000.0: 0.00035585, 1535483400000.0: 0.00035782, 1535483700000.0: 0.00035775, 1535484000000.0: 0.00035735, 1535484300000.0: 0.00035731, 1535484600000.0: 0.00036035, 1535484900000.0: 0.00036031}, 'volume': {1535455200000.0: 240217.0, 1535455500000.0: 26273.0, 1535455800000.0: 10973.0, 1535456100000.0: 30723.0, 1535456400000.0: 10190.0, 1535456700000.0: 8944.0, 1535457000000.0: 34252.0, 1535457300000.0: 74536.0, 1535457600000.0: 55832.0, 1535457900000.0: 38786.0, 1535458200000.0: 40491.0, 1535458500000.0: 6893.0, 1535458800000.0: 15206.0, 1535459100000.0: 67365.0, 1535459400000.0: 40610.0, 1535459700000.0: 4145.0, 1535460000000.0: 175002.0, 1535460300000.0: 16854.0, 1535460600000.0: 44394.0, 1535460900000.0: 54773.0, 1535461200000.0: 76411.0, 1535461500000.0: 12062.0, 1535461800000.0: 9966.0, 1535462100000.0: 6800.0, 1535462400000.0: 72687.0, 1535462700000.0: 53564.0, 1535463000000.0: 153724.0, 1535463300000.0: 63438.0, 1535463600000.0: 344991.0, 1535463900000.0: 314195.0, 1535464200000.0: 351383.0, 1535464500000.0: 155287.0, 1535464800000.0: 61759.0, 1535465100000.0: 23536.0, 1535465400000.0: 54700.0, 1535465700000.0: 211079.0, 1535466000000.0: 53125.0, 1535466300000.0: 92141.0, 1535466600000.0: 179726.0, 1535466900000.0: 40507.0, 1535467200000.0: 143728.0, 1535467500000.0: 626363.0, 1535467800000.0: 26724.0, 1535468100000.0: 15337.0, 1535468400000.0: 282174.0, 1535468700000.0: 114309.0, 1535469000000.0: 83910.0, 1535469300000.0: 44634.0, 1535469600000.0: 2731.0, 1535469900000.0: 104236.0, 1535470200000.0: 36578.0, 1535470500000.0: 2001.0, 1535470800000.0: 95456.0, 1535471100000.0: 12876.0, 1535471400000.0: 102063.0, 1535471700000.0: 67722.0, 1535472000000.0: 15364.0, 1535472300000.0: 20762.0, 1535472600000.0: 76093.0, 1535472900000.0: 216062.0, 1535473200000.0: 61728.0, 1535473500000.0: 138228.0, 1535473800000.0: 47878.0, 1535474100000.0: 24147.0, 1535474400000.0: 38452.0, 1535474700000.0: 56124.0, 1535475000000.0: 31672.0, 1535475300000.0: 38447.0, 1535475600000.0: 57421.0, 1535475900000.0: 15443.0, 1535476200000.0: 45911.0, 1535476500000.0: 9502.0, 1535476800000.0: 20130.0, 1535477100000.0: 8099.0, 1535477400000.0: 39866.0, 1535477700000.0: 52857.0, 1535478000000.0: 111575.0, 1535478300000.0: 110202.0, 1535478600000.0: 224006.0, 1535478900000.0: 52740.0, 1535479200000.0: 5971.0, 1535479500000.0: 22183.0, 1535479800000.0: 44995.0, 1535480100000.0: 7579.0, 1535480400000.0: 93339.0, 1535480700000.0: 34915.0, 1535481000000.0: 33521.0, 1535481300000.0: 37200.0, 1535481600000.0: 39763.0, 1535481900000.0: 110198.0, 1535482200000.0: 38135.0, 1535482500000.0: 3101.0, 1535482800000.0: 39594.0, 1535483100000.0: 73192.0, 1535483400000.0: 54496.0, 1535483700000.0: 22821.0, 1535484000000.0: 18165.0, 1535484300000.0: 29396.0, 1535484600000.0: 192780.0, 1535484900000.0: 30962.0}}
    df = candles_to_df(data)
    print(df)
    print(df.dtypes)
