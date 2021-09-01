package replayer;

import framework.core.Game;
import framework.core.GameObject;
import framework.utils.Vector2d;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.util.LinkedList;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 26/01/12
 */
public class AppletView extends JComponent
{

    //References to other entities:
    private AppletGame m_game;

    //Size of the map
    private Dimension m_size;

    //Size of the applet image
    private Dimension m_maxSize;

    //Some fonts for texts
    private Font m_font;
    private Font m_font2;
    private Font m_font3;

    private boolean m_startText;
    private boolean m_startPressed;

    //List of positions, for drawing
    private LinkedList<Vector2d> m_positions;

    //Colors:
    //Paper easy-read format:
    /*private Color background = Color.white;
    private Color trajectory = Color.black;
    private Color obstacle = Color.darkGray;
    private Color finalResult = Color.yellow;
    private Color fontColor = Color.red;         */

    //Execution format:
    private Color outsideBackground = new Color(52,154,217);
    private Color background = Color.black;
    private Color trajectory = Color.white;
    private Color obstacle = Color.darkGray;
    private Color finalResult = Color.yellow;
    private Color startText = Color.yellow;
    private Color fontColor = Color.MAGENTA;

    private Graphics2D bufferGraphics;
    private Image offscreen;

    //first draw;
    private boolean m_firstDraw;

    //Map image, buffered
    private BufferedImage m_mapImage;


    public AppletView(AppletGame a_game, Dimension a_size, Dimension a_maxSize) {
        m_game = a_game;
        m_size = a_size;
        m_startText = m_startPressed =false;
        m_maxSize = a_maxSize;
        m_font = new Font("Courier", Font.PLAIN, 16);
        m_font2 = new Font("Courier", Font.BOLD, 18);
        m_font3 = new Font("Courier", Font.BOLD, 18);
        m_positions = new LinkedList<Vector2d>();
        m_firstDraw = true;
        m_mapImage = null;
    }

    public void paintComponent(Graphics gx)
    {
        if(offscreen==null)
    	{
    		offscreen=createImage(this.getPreferredSize().width,this.getPreferredSize().height);
    		bufferGraphics= (Graphics2D) offscreen.getGraphics();
    	}

        Vector2d freeSpace = new Vector2d(this.getPreferredSize().width - m_size.width, this.getPreferredSize().height - m_size.height -50);
        //System.out.println("freeSpace (" + freeSpace + "), m_size (" + m_size + "), preferredSize: (" + this.getPreferredSize());

        //MARGIN:
        bufferGraphics.setColor(outsideBackground);
        bufferGraphics.fillRect(0, 0, (int) (freeSpace.x*0.5), this.getPreferredSize().height);   // Left margin
        bufferGraphics.fillRect(this.getPreferredSize().width - (int) (freeSpace.x*0.5) -1, 0, this.getPreferredSize().width, this.getPreferredSize().height); //Right margin
        bufferGraphics.fillRect(0, m_size.height+(int) (freeSpace.y*0.5), this.getPreferredSize().width, this.getPreferredSize().height); //Bottom margin
        bufferGraphics.fillRect(0, 0, this.getPreferredSize().width, (int) (freeSpace.y*0.5)); //Top margin

        bufferGraphics.translate((int) (freeSpace.x*0.5), (int) (freeSpace.y*0.5));
        //bufferGraphics.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        bufferGraphics.setColor(background);
        bufferGraphics.fillRect(0, 0, m_size.width, m_size.height);


        AppletMap map = m_game.getMap();

        //Draw the map.
        if(m_firstDraw)
        {
            m_mapImage = new BufferedImage(m_size.width, m_size.height,BufferedImage.TYPE_INT_RGB);
            Graphics2D gImage = m_mapImage.createGraphics();
            for(int i = 0; i < map.getMapChar().length; ++i)
            {
                for(int j = 0; j < map.getMapChar()[i].length; ++j)
                {
                    if(map.isObstacle(i,j))
                    {
                        gImage.setColor(obstacle);
                        gImage.fillRect(i,j,1,1);
                    }
                }
            }
            m_firstDraw = false;

        } else {

            bufferGraphics.drawImage(m_mapImage,0,0,null);

        }



        this.setStartText(!m_game.hasStarted() && m_startPressed);

        synchronized (Game.class) {
            for (GameObject go : m_game.getGameObjects()) {
                go.draw(bufferGraphics);
            }
        }

        AppletShip gameShip = m_game.getShip();
        if(gameShip.ps.x != gameShip.s.x || gameShip.ps.y != gameShip.s.y)
        {
            m_positions.add(gameShip.s.copy());
        }

        //Draw the trajectory
        bufferGraphics.setColor(trajectory);
        Vector2d oldPos = null;
        for(Vector2d pos : m_positions)
        {
            if(oldPos == null)
            {
                oldPos = pos;
            }else
            {
                bufferGraphics.drawLine((int)Math.round(oldPos.x),(int)Math.round(oldPos.y),(int)Math.round(pos.x),(int)Math.round(pos.y));
                oldPos = pos;
            }
        }

        //Paint stats of the m_game.
        paintStats(bufferGraphics, map);

        gx.drawImage(offscreen,0,0,this);
        bufferGraphics.translate((int) -(freeSpace.x*0.5), (int) -(freeSpace.y*0.5));
    }

    private void paintStats(Graphics2D g, AppletMap a_map)
    {
        g.setColor(fontColor);
        g.setFont(m_font);
        g.drawString("Total time: " + m_game.getTotalTime(), 10, 20);
        g.drawString("Time left: " + m_game.getStepsLeft(), 10, 40);
        g.drawString("Waypoints: " + m_game.getWaypointsVisited() + "/" + m_game.getNumWaypoints(), 10, 60);

        if(m_startText)
        {
            g.setColor(startText);
            g.setFont(m_font3);
            g.drawString("Use the cursor keys to move the ship", 50, 210);
        }


        if(m_game.getWaypointsLeft() == 0)
        {
            g.setColor(finalResult);
            g.setFont(m_font2);
            g.drawString("Final score: " + (a_map.getNumWaypoints()-m_game.getWaypointsLeft()) + " waypoints "
                    + "in " + m_game.getTotalTime() + " steps.", 10, 80);

        }else if(m_game.getStepsLeft() <= 0)
        {
            g.setColor(finalResult);
            g.setFont(m_font2);
            g.drawString("Time out. Final score: " + (a_map.getNumWaypoints()-m_game.getWaypointsLeft()) +
                    " waypoints", 10, 100);
            g.drawString(" in " + m_game.getTotalTime() + " steps.", 10, 120);
        }
    }

    public void setStartText(boolean a_text)
    {
        m_startText = a_text;
    }

    public void setStartPressed(boolean a_pressed)
    {
        m_startPressed = a_pressed;
        m_startText = m_startPressed =false;
    }

    public void reset()
    {
        m_positions = new LinkedList<Vector2d>();
        m_firstDraw = true;
        m_mapImage = null;
    }

    public Dimension getPreferredSize() {
        return m_maxSize;
    }

    public void setMapSize(Dimension a_ms) {m_size = a_ms;}

}
