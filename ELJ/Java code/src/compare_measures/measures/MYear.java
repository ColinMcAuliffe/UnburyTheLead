package compare_measures.measures;

import java.util.Vector;

import compare_measures.Draw;

public class MYear extends aMeasure {

	@Override
	public String getName() {
		return "Election year";
	}

	@Override
	public String getAbbr() {
		return "Year";
	}

	@Override
	public double getScore(Draw draw) {
		return draw.year;
	}

	@Override
	public double getLowerBound() {
		return 1970;
	}

	@Override
	public double getUpperBound() {
		return 2018;
	}
}
