with Carrier as c:{
	in Leftward direction:{
		knit Front_Needles[0:pattern_width];
	}
	in Rightward direction:{
		knit Back_Needles[0:pattern_width];
	}
	in Leftward direction:{
		knit Loops;
	}
	releasehook;
}
cut c;
