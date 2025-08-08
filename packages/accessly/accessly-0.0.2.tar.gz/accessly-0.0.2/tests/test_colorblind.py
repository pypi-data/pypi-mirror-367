import accessly as av
import matplotlib.pyplot as plt
import numpy as np


def test_default():
	av.configure(
		colorblind={
		}
    )

	x = np.arange(0,10,1)
	fig, ax = plt.subplots(figsize=(5,5))
	for i in range(2):
		ax.plot(x, x+i)
	ax.set_xlabel('X values')
	ax.set_ylabel('Y values')
	lines = ax.get_lines()
	plt.show(block=False)
	assert lines[0].get_color() == '#1f77b4'
	assert lines[1].get_color() == '#ff7f0e'
	
def test_redgreen():
	av.configure(
		colorblind={
			'type' : 'redgreen'
		}
    )

	x = np.arange(0,10,1)
	fig, ax = plt.subplots(figsize=(5,5))
	for i in range(2):
		ax.plot(x, x+i)
	ax.set_xlabel('X values')
	ax.set_ylabel('Y values')
	lines = ax.get_lines()
	plt.show(block=False)
	assert lines[0].get_color() != '#1f77b4'
	assert lines[1].get_color() != '#ff7f0e'
	
def test_blueyellow():
	av.configure(
		colorblind={
			'type' : 'blueyellow'
		}
    )

	x = np.arange(0,10,1)
	fig, ax = plt.subplots(figsize=(5,5))
	for i in range(2):
		ax.plot(x, x+i)
	ax.set_xlabel('X values')
	ax.set_ylabel('Y values')
	lines = ax.get_lines()
	plt.show(block=False)
	assert lines[0].get_color() != '#1f77b4'
	assert lines[1].get_color() != '#ff7f0e'
	
def test_invalid():
	av.configure(
		colorblind={
			'type' : 'invalid'
		}
    )

	x = np.arange(0,10,1)
	fig, ax = plt.subplots(figsize=(5,5))
	for i in range(2):
		ax.plot(x, x+i)
	ax.set_xlabel('X values')
	ax.set_ylabel('Y values')
	lines = ax.get_lines()
	plt.show(block=False)
	assert lines[0].get_color() != '#1f77b4'
	assert lines[1].get_color() != '#ff7f0e'

if __name__ == '__main__':
	test_default()
	test_redgreen()
	test_blueyellow()
	test_invalid()