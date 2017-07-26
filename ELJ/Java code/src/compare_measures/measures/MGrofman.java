package compare_measures.measures;

import compare_measures.Draw;

public class MGrofman extends aMeasure {

	@Override
	public String getName() {
		return "Grofman King Asymmetry";
	}

	@Override
	public String getAbbr() {
		return "GA";
	}

	@Override
	public double getScore(Draw draw) {
		return getSeatFraction(draw,0.5);
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
