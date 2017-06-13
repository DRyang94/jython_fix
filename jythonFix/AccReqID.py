# package com.btcchina.fix;

import quickfix.StringField

class AccReqID(quickfix.StringField):
    def __init__(self,data = ''):
        self.serialVersionUID = 2330170161864948797L;
        if data == '':
            quickfix.StringField.__init__(self,8000)
        else:
            quickfix.StringField.__init__(self,FIELD,data)

	private static final long serialVersionUID = 2330170161864948797L;
	public static final int FIELD = 8000;
	
	public AccReqID() {
		super(8000);
	}

	 public AccReqID(String data) {
	        super(FIELD, data);
	    }
}
