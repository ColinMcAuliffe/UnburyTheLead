package compare_measures.measures;

import compare_measures.Draw;

public class MLopsidedMargins extends aMeasure {

	@Override
	public String getName() {
		return "Lopsided Margins";
	}

	@Override
	public String getAbbr() {
		return "LM";
	}

	@Override
	public double getScore(Draw draw) {
		return 0;
	}

	@Override
	public double getLowerBound() {
		return -1;
	}

	@Override
	public double getUpperBound() {
		return 1;
	}
}
