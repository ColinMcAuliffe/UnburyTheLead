package new_metrics;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;

public class DrawScaled {
	Graphics2D graphics = null;
	double scalex,scaley,strokescale = 1;
	Font smallFont = null;
	Font largeFont = null;
	public DrawScaled( Graphics2D _graphics, double _scalex, double _scaley, double _strokescale) {
		scalex = _scalex;
		scaley = _scaley;
		strokescale = _strokescale;
		graphics = _graphics;
		smallFont = graphics.getFont();
		largeFont = new Font(smallFont.getFontName(),smallFont.getStyle(),(int)(smallFont.getSize()*_strokescale));
		graphics.setFont(largeFont);
	}
	public void setColor(Color c) { graphics.setColor(c); }

	public void drawString(String s, double x, double y) {
		graphics.drawString(s,tx(x),ty(y));
	}
	
	public void drawLine(double x0, double y0, double x1, double y1) {
		graphics.drawLine(tx(x0),ty(y0),tx(x1),ty(y1));
	}
	
	public void drawOval(double x0, double y0, double x1, double y1) {
		graphics.drawOval(tx(x0),ty(y0),tx(x1),ty(y1));
	}
	
	public void fillOval(double x0, double y0, double x1, double y1) {
		graphics.fillOval(tx(x0),ty(y0),tx(x1),ty(y1));
	}
	
	public void fillRect(double x0, double y0, double x1, double y1) {
		graphics.fillRect(tx(x0),ty(y0),tx(x1),ty(y1));
	}
	
	public void drawRect(double x0, double y0, double x1, double y1) {
		graphics.drawRect(tx(x0),ty(y0),tx(x1),ty(y1));
	}
	public int stringWidth(String s) {
		return (int)Math.round(graphics.getFontMetrics().stringWidth(s)/scalex);
	}

	public Graphics2D getGraphics() { return graphics; }
	
    public int tx(double x) {
    	return (int)Math.round(x *scalex);
    }
    public int ty(double x) {
    	return (int)Math.round(x * scaley);
    }
    public int ts(double x) {
    	return (int)Math.round(x * strokescale);
    }

}
