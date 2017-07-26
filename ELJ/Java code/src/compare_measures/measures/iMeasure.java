package compare_measures.measures;

import java.util.*;

import compare_measures.*;

public interface iMeasure {
	HashMap<String, PiecewiseLinearMonotonicCurve> curves = new HashMap<String, PiecewiseLinearMonotonicCurve>();
	
	public String getName();
	public String getAbbr();
	public double getScore(Draw draw);
	public void scoreDraws(Vector<Draw> draws);
	public double getLowerBound();
	public double getUpperBound();
}
