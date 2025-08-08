with Carrier as c:{
	print reverse;
	in Leftward direction:{
		tuck Front_Needles[1:pattern_width:2];
	}
	print reverse;
	in Rightward direction:{
		tuck Front_Needles[0:pattern_width:2];
	}
	print reverse;
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
