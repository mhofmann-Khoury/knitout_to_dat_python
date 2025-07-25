import cast_ons;

with Carrier as c:{
	in Leftward direction:{
		tuck Front_Needles[1:pattern_width:2];
		tuck Back_Needles[0:pattern_width:2];
	}
	in reverse direction:{
		tuck Front_Needles[0:pattern_width:2];
		tuck Back_Needles[1:pattern_width:2];
	}
	releasehook;
	for _ in range(pattern_height):{
		in reverse direction:{
			knit Loops;
		}
		in reverse direction:{
			knit Loops;
		}
	}
	with Rack as 1:{
		 for _ in range(pattern_height):{
			in reverse direction:{
				knit Loops;
			}
			in reverse direction:{
				knit Loops;
			}
		}
	}
	with Rack as -1:{
		 for _ in range(pattern_height):{
			in reverse direction:{
				knit Loops;
			}
			in reverse direction:{
				knit Loops;
			}
		}
	}

	with Rack as 0:{
		 for _ in range(pattern_height):{
			in reverse direction:{
				knit Loops;
			}
			in reverse direction:{
				knit Loops;
			}
		}
	}
}
