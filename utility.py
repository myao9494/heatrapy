from scipy import interpolate

def create_function(ds_x,ds_y):
    """関数を作成する
    関数は、funcrion(xの値).tolist()　でyの値を取得（線形補間してくれる）

    Arguments:
        ds_x {pandas data series} -- 関数のxです
        ds_y {pandas data series} -- 関数のyです

    Returns:
        funcrion -- 関数を返します
    """    
    f = interpolate.interp1d(ds_x, ds_y)
    return f