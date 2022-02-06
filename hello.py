import numpy as np
from numpy.random import default_rng
import streamlit as st
import pandas as pd
import time
from datetime import datetime



# Make Fake Price Path

@st.cache
def gen_GBM(mu:float , sigma: float, T: float, N: int, S0: float):
	"""
	Make fake stock path
	S_{n} = S0 * exp(sum_{i = 1}^{n} Z_{i} * sqrt(dt))
	"""
	dt = T / N
	St = np.zeros((N + 1))
	St[0] = S0

		 # random number generator
	# make brownian increments 		
	Zs = st.session_state['rng'].standard_normal((N)) * sigma * np.sqrt(dt)
	# make fake price path
	St[1:] = S0 * np.exp(np.cumsum(mu * dt  + Zs))
	return St


def gen_GBM2(mu:float , sigma: float, T: float, N: int, S0: float, rng = default_rng()):
	"""
	Make fake stock path
	S_{n} = S0 * exp(sum_{i = 1}^{n} Z_{i} * sqrt(dt))
	"""
	dt = T / N
	return np.exp(mu * dt + rng.standard_normal() * np.sqrt(dt) * sigma)
	






def buy_action():
	hold = st.session_state["holders"].get(st.session_state["tick_time"] // st.session_state['COMMITTMENT'], 0)
	if not hold:
		st.session_state["trades"] += [{"date":datetime.now(), "price":st.session_state['path'][-1], "sign":1}]

def sell_action():
	hold = st.session_state["holders"].get(st.session_state["tick_time"] // st.session_state['COMMITTMENT'], 0)
	if not hold:
		st.session_state["trades"] += [{"date":datetime.now(), "price":st.session_state['path'][-1], "sign": -1}]
	


def hold_action():
	st.session_state["holders"][st.session_state["tick_time"] // st.session_state['COMMITTMENT'] + 1] = True


st.title("HODL Demo")

if __name__ == '__main__':
	st.write("""
	# HODLcoin Demo

	HODLcoin is a Proof-of-Concept for a smart contract that has the potential use cases:

	1. Deterring pump-and-dump schemes; Improving transparecy
	2. For asset managers, deterring cash outflows

	## How it works / Concept:

	The HODLcoin concept can be as  *time-linked* deposit. ***Time Linked Deposits*** (see [here](https://www.investopedia.com/terms/t/timedeposit.asp)) are a type of derivative that offers 

	## Demo

	You play the role of a investor in ICHackcoin
	""")


	N = 1000
	N2 = 100

	if 'trades' not in st.session_state:
		st.session_state['trades'] = []

	if 'rng' not in st.session_state:
		st.session_state['rng'] = default_rng()

	if 'holders' not in st.session_state:
		st.session_state['holders'] = {}

	if 'tick_time' not in st.session_state:
		st.session_state['tick_time'] = N2

	st.session_state['COMMITTMENT'] = 30

	
	
	path = gen_GBM(5, 3, 1, N, 1)
	if 'path' not in st.session_state:
		st.session_state['path'] = list(path[:N2])

	# st.write(path)
	handle = st.line_chart(st.session_state['path'])
	with st.form(key='form1'):
		submit_button = st.form_submit_button(label='HODL')
	with st.form(key='form2'):
		submit_button2 = st.form_submit_button(label='BUY')
	with st.form(key='form3'):
		submit_button3 = st.form_submit_button(label='SELL')
	

	if submit_button:
		hold_action()
	if submit_button2:
		buy_action()

	if submit_button3:
		sell_action()


	st.write(pd.DataFrame(st.session_state["trades"]))



	
	
	logtxtbox = st.empty()
	logtxt = 'start'
	if st.session_state['holders'].get(st.session_state['tick_time'] // st.session_state['COMMITTMENT'], 0):
		HODL = "CURRENTLTY HODLING"
	else:
		HODL = ""
	logtxtbox.text_area("Logging: ",f"{st.session_state['tick_time'], st.session_state['holders']} HODLING: {HODL}", height = 50)
	
	
	handle2 = st.write(f"### Number of people HODLers: {st.session_state['tick_time'], st.session_state['holders']}")
	while st.session_state['tick_time'] < (N - N2):
		st.session_state['path'] += list([path[N2 + st.session_state['tick_time']]])
		handle.line_chart(st.session_state['path'])
		st.session_state['tick_time'] += 1
		if st.session_state['holders'].get(st.session_state['tick_time'] // st.session_state['COMMITTMENT'], 0):
			HODL = "CURRENTLTY HODLING"
		else:
			HODL = ""
		logtxtbox.text_area("Logging: ", f"{st.session_state['tick_time'], st.session_state['holders']} HODLING: {HODL}", height=50)



	


	





	
