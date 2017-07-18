package compare_measures.measures;

import compare_measures.Draw;

public class MGrofman extends aMeasure {

	@Override
	public String getName() {
		return "Grofman King";
	}

	@Override
	public String getAbbr() {
		return "GK";
	}

	@Override
	public double getScore(Draw draw) {
		return draw.popular_pct;
	}

	@Override
	public double getLowerBound() {
		return 0;
	}

	@Override
	public double getUpperBound() {
		return 1;
	}
}
