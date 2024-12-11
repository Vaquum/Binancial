def histogram(data, x, bins=10):

    '''Draws vanilla histogram for any x.
    
    data | dataframe | the dataset
    x | str or list | column/s to be used for the histogram
    bins | int | number of bins to be drawn
    
    '''

    import astetik

    astetik.hist(data, x=x, bins=bins)
