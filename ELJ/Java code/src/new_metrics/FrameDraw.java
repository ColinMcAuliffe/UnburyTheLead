package new_metrics;

import java.util.*;

import javax.swing.*;
import javax.swing.table.*;

import org.apache.commons.math3.distribution.BetaDistribution;

import util.Pair;

import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;

public class FrameDraw extends JFrame {
	int size = 1000;

	public PiePanel panel = null;
	
	public FrameDraw() {
		super();
		initComponents();
	}

	private void initComponents() {
		getContentPane().setLayout(null);
		setSize(size,size);
		setTitle("Draw");
		
		panel = new PiePanel();
		panel.setBounds(0, 0, 1000, 1000);
		getContentPane().add(panel);
	}
	
	BetaDistribution dist = null;
	Vector<BetaDistribution> dists = null;
	double[] seats = null;
	public Vector<Pair<Double, Double>> bins = null;
	
	class PiePanel extends JPanel {
		
	    public void paintComponent(Graphics graphics0) {
	    	try {
	            Graphics2D graphics = (Graphics2D)graphics0;

	            double fsaa=2;
	            Dimension d = this.getSize();
	    		double width = d.getWidth();
	    		double height = d.getHeight();

		        graphics.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_BICUBIC);
		        graphics.setRenderingHint(RenderingHints.KEY_RENDERING,RenderingHints.VALUE_RENDER_QUALITY);
		        graphics.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
		        graphics.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

			    super.paintComponent(graphics);
			    
			    graphics.setColor(Color.white);
			    graphics.fillRect(0, 0, size, size);
			    width = size;
			    height = size;
			    
			    BufferedImage image = drawOnImage(width*fsaa,height*fsaa,fsaa);
			    //BufferedImage image = drawOnImage(width,height,fsaa);
			    
			    graphics.drawImage(image
			    		,0,0,(int)width,(int)height
			    		//,0,0,(int)width*2,(int)height*2
			    		,null);
	    	} catch (Exception ex) {
	    		ex.printStackTrace();
	    	}
	    }
	    
    	public BufferedImage drawOnImage(double _width, double _height, double fsaa) {
    		try {
	
	    		BufferedImage off_Image =
		        		  new BufferedImage(
		        				  (int) (_width), 
		        				  (int) (_height), 
		        		          BufferedImage.TYPE_INT_ARGB
		        		          );
		        Graphics2D graphics2 = off_Image.createGraphics();
		        

		        graphics2.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_BICUBIC);
		        graphics2.setRenderingHint(RenderingHints.KEY_RENDERING,RenderingHints.VALUE_RENDER_QUALITY);
		        graphics2.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
		        graphics2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
		        graphics2.setStroke(new BasicStroke((int)fsaa));
		        graphics2.setFont(new Font("Arial",0,20));
		        
		        DrawScaled graphics = new DrawScaled(graphics2,_width/1000.0,_height/1000.0,fsaa);
		        graphics.setColor(Color.white);
		        graphics.fillRect(0, 0, (int)_width, (int)_height);
		        
		        
			    graphics.setColor(Color.gray);
			    if( bins != null) {
			    	int length = (int)(size-100)/bins.size();
			    	int min_x = -50;
			    	int x = 50;
			    	
			    	for( int i = 0; i < bins.size(); i++) {
			    		int height = (int)(bins.get(i).b*size);
			    		if( bins.get(i).a <= 0) {
						    graphics.setColor(Color.red);
						    if( bins.get(i).a == 0) {
						    	graphics.setColor(Color.gray);
						    }
			    			
			    		} else {
						    graphics.setColor(Color.blue);

			    		}

			    		
			    		graphics.fillRect(x, (size-100)-height, length, height);
			    		String s = ""+(Math.round(bins.get(i).a * 1000.0)/1000.0);
			    		int textx = x + length/2 - graphics.stringWidth(s)/2;
			    		if( textx > min_x) {
			    			graphics.drawString(s, textx, size-80);
			    			min_x = textx + graphics.stringWidth(s+"  ");
			    		}
			    		//graphics.drawString(s, textx, size-80);
			    		x += length;
			    	}
			    	
			    }
			    if( seats != null) {
			    	int min_x = 0;
			    	int length = (int)((size-100)/seats.length);
			    	int x = 50;
			    	for( int i = seats.length-1; i >= 0; i--) {
			    		int height = (int)(seats[i]*size);
			    		if( x < size/2) {
						    graphics.setColor(Color.red);
						    if( x+length > size/2) {
						    	graphics.setColor(Color.gray);
						    }
			    			
			    		} else {
						    graphics.setColor(Color.blue);

			    		}
			    		graphics.fillRect(x, size-100-height, length, height);
			    		String s = ""+i+" rep";
			    		String s2 = ""+(seats.length-i-1)+" dem";
			    		int textx = x + length/2 - graphics.stringWidth(s)/2;
			    		if( textx > min_x) {
			    			graphics.drawString(s, textx, size-80);
			    			graphics.drawString(s2, textx, size-60);
			    			min_x = textx + (graphics.stringWidth(s+"  ") > graphics.stringWidth(s2+"   ") ? graphics.stringWidth(s+"   ") : graphics.stringWidth(s2+"   "));
			    			//min_x = textx + graphics.stringWidth(s2+"  ");
			    		}
			    		x += length;
			    	}
			    }
 			    if( true) {
 				    if( dists != null) {
 					    double inc = 0.0001;
 				    	for( BetaDistribution dist : dists) {
 					    	double x = 0;
 					    	double last_x = 0;
 					    	double last_y = 0;
 					    	while(x <= 1) {
 					    		double y = dist.density(1-x);
 					    		if( x > 0.5) {
 								    graphics.setColor(Color.red);
 					    			
 					    		} else {
 								    graphics.setColor(Color.blue);

 					    		}
 					    		
 					    		graphics.drawLine(transformx(last_x),transformy(last_y),transformx(x),transformy(y));
 					    		
 					    		last_y = y;
 					    		last_x = x;
 					    		x += inc;
 					    	}
 				    	}
 					    graphics.setColor(Color.black);
 					    graphics.drawString("Popular vote", (size/2)-graphics.stringWidth("Popular vote")/2, size-80);
 						
 					    graphics.setColor(Color.blue);
 						graphics.drawString("Democratic seats", size-graphics.stringWidth("Democratic seats")-10, size-80);
 						
 					    graphics.setColor(Color.red);
 						graphics.drawString("Republican seats", 10, size-80);
 				    }
 				    graphics.setColor(Color.black);
			    
				    if( dist != null) {
					    double inc = 0.0001;
				    	double x = 0;
				    	double last_x = 0;
				    	double last_y = 0;
				    	while(x <= 1) {
				    		double y = dist.density(1-x);
				    		
				    		graphics.drawLine(transformx(last_x),transformy(last_y),transformx(x),transformy(y));
				    		
				    		last_y = y;
				    		last_x = x;
				    		x += inc;
				    	}
				    	/*
					    graphics.drawString("Popular vote", (size/2)-graphics.stringWidth("Popular vote")/2, size-80);
						
					    graphics.setColor(Color.blue);
						graphics.drawString("Democratic seats", 10, size-80);
						
					    graphics.setColor(Color.red);
						graphics.drawString("Republican seats", size-graphics.stringWidth("Republican seats")-20, size-80);
						*/
				    }
			    }
	
	    		return off_Image;
	    	} catch (Exception ex) {
	    		System.out.println("ex csafs "+ex);
	    		ex.printStackTrace();
	    		System.exit(0);
	    		return null;
	    	}
	    	
	    	
		}
		double transformx(double x) {
    		//return Math.round(2.0*(500-x*500));
    		return 2.0*(500-x*500);
    	}
		double transformy(double y) {
    		//return Math.round(2.0*(-y*5+400));
    		return 2.0*(-y*5+450);
    	}
	}
	class DrawScaled {
		Graphics2D graphics = null;
		double scalex,scaley,strokescale = 1;
		Font smallFont = null;
		Font largeFont = null;
		DrawScaled( Graphics2D _graphics, double _scalex, double _scaley, double _strokescale) {
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

}