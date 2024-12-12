class Accountant:

    '''Accountant class is used to keep track of account information'''
    
    def __init__(self, start_usdt):
        
        '''Initializes the accountant object.
        
        start_usdt | int | starting usdt balance
        '''
        
        self.id = 0
        
        self.account = self._init_account(credit_usdt=start_usdt,
                                          debit_usdt=None)
        
        self.update_id()
        
    def _init_account(self, credit_usdt, debit_usdt):
        
        '''Initializes the account with the starting balance.
        
        credit_usdt | int | starting usdt balance
        debit_usdt | int | starting usdt balance
        '''
        
        account = {'id': [self.id],
                   'action': ['hold'],
                   'timestamp': [0],
                   'credit_usdt': [credit_usdt],
                   'debit_usdt': [0],
                   'amount_bought_btc': [0],
                   'amount_sold_btc': [0],
                   'buy_price_usdt': [0],
                   'sell_price_usdt': [0],
                   'total_usdt': [credit_usdt],
                   'total_btc': [0]}
        
        return account
    
    def update_account(self,
                       action,
                       timestamp,
                       amount,
                       price_usdt):
        
        '''Updates the account information based on the action taken.
        
        action | str | 'buy', 'sell', or 'hold'
        timestamp | datetime | current timestamp
        amount | int | amount of BTC
        price_usdt | float | current price of the asset
        '''
        
        if action == 'buy':
            
            if amount > self.account['total_usdt'][-1]:
                debit_usdt = self.account['total_usdt'][-1]
            else:
                debit_usdt = amount
            
            credit_usdt = 0
            buy_price_usdt = price_usdt
            sell_price_usdt = 0
        
        elif action == 'sell':
            
            if self.account['total_btc'][-1] == 0:
                credit_usdt = 0
            elif (amount / price_usdt) > self.account['total_btc'][-1]:
                credit_usdt = self.account['total_btc'][-1] * price_usdt
            else:
                credit_usdt = amount
            
            debit_usdt = 0
            buy_price_usdt = 0
            sell_price_usdt = price_usdt
                
        elif action == 'hold':
            
            debit_usdt = 0    
            credit_usdt = 0
            buy_price_usdt = 0
            sell_price_usdt = 0
            
        self.account['id'].append(self.id)
        self.account['action'].append(action)
        self.account['timestamp'].append(timestamp)
        self.account['credit_usdt'].append(credit_usdt)
        self.account['debit_usdt'].append(debit_usdt)
        self.account['amount_bought_btc'].append(round(debit_usdt / price_usdt, 4))
        self.account['amount_sold_btc'].append(round(credit_usdt / price_usdt, 4))
        self.account['buy_price_usdt'].append(buy_price_usdt)
        self.account['sell_price_usdt'].append(sell_price_usdt)
    
        total_btc = sum(self.account['amount_bought_btc']) - sum(self.account['amount_sold_btc'])
        total_usdt = sum(self.account['credit_usdt']) - sum(self.account['debit_usdt'])
        
        self.account['total_btc'].append(round(total_btc, 4))        
        self.account['total_usdt'].append(round(total_usdt, 2))
        
    def update_id(self):
        
        '''Will increment id by one. This has to be run always before
        updating account or book.'''
        
        self.id += 1
        