package compare_measures.measures;

import java.util.Vector;

import compare_measures.Draw;

public class MNDistricts extends aMeasure {

	@Override
	public String getName() {
		return "Number of Districts";
	}

	@Override
	public String getAbbr() {
		return "Districts";
	}

	@Override
	public double getScore(Draw draw) {
		return draw.centered_district_pcts.length;
	}

	@Override
	public double getLowerBound() {
		return 0;
	}

	@Override
	public double getUpperBound() {
		return 55;
	}
}
