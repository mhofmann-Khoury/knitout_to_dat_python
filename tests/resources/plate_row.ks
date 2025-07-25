with Carrier as 1:{
	in Leftward direction:{
		knit Front_Needles[0:6];
	}
	in reverse direction:{
		knit Loops;
	}
	releasehook;
}
with Carrier as 2:{
	in reverse direction:{
		knit Loops;
	}
	in reverse direction:{
		knit Loops;
	}
	releasehook;
}
with Carrier as [1,2]:{
	in Leftward direction:{
		knit Loops;
	}
	in reverse direction:{
		knit Loops;
	}
}
with Carrier as [2,1]:{
	in reverse direction:{
		knit Front_Loops[2:];
	}
}
with Carrier as [1,2]:{
	in current direction:{
		knit Front_Loops[0:2];
	}
}
with Carrier as [2,1]:{
	in reverse direction:{
		knit Front_Loops[0:2];
	}
}
with Carrier as [1,2]:{
	in current direction:{
		knit Front_Loops[2:];
	}
}
