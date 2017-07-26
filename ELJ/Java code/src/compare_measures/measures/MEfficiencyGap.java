package compare_measures.measures;

import compare_measures.Draw;

public class MEfficiencyGap extends aMeasure {

	@Override
	public String getName() {
		return "Efficiency gap";
	}

	@Override
	public String getAbbr() {
		return "EG";
	}

	@Override
	public double getScore(Draw draw) {
		return (getSeatFraction(draw,draw.popular_pct) - 0.5) - 2*(draw.popular_pct-0.5);
	}

	@Override
	public double getLowerBound() {
		return -0.5;
	}

	@Override
	public double getUpperBound() {
		return 0.5;
	}
}
