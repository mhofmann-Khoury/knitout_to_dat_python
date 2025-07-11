with Carrier as c:{
	in Leftward direction:{
		tuck Front_Needles[1:pattern_width:2];
	}
	in Rightward direction:{
		tuck Front_Needles[0:pattern_width:2];
	}
	in reverse direction:{
		knit Loops;
	}
	in reverse direction:{
		knit Loops;
	}
	releasehook;
	for _ in range(pattern_height):{
		in reverse direction:{
			knit Loops;
		}
	}
}
