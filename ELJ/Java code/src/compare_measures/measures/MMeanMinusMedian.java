package compare_measures.measures;

import compare_measures.Draw;

public class MMeanMinusMedian extends aMeasure {

	@Override
	public String getName() {
		return "Nagle area";
	}

	@Override
	public String getAbbr() {
		return "Vote";
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
