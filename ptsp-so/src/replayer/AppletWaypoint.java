package replayer;

import framework.core.GameObject;
import framework.utils.Vector2d;

import java.awt.*;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 26/01/12
 */
public class AppletWaypoint extends GameObject
{
    //Collected or not.
    protected boolean collected;

    //radius of the waypoint.
    public static int RADIUS = 4;

    private AppletGame m_appletGame;

    private AppletWaypoint()
    {
    }

    //Constructor.
    public AppletWaypoint(AppletGame game, Vector2d s)
    {
        m_appletGame = game;
        this.s = s;
        this.collected = false;
        this.radius = RADIUS;
    }

    public void update() {
        //Nothing to do here.
    }

    //Draws the waypoint.
    public void draw(Graphics2D g)
    {
        if(!collected)
            g.setColor(Color.red);
        else
            g.setColor(Color.blue);

        int drawRadius = m_appletGame.getShip().SHIP_RADIUS * radius;
        g.fillOval((int) (s.x - drawRadius*0.5),(int) (s.y - drawRadius*0.5),drawRadius,drawRadius);

        g.setColor(Color.yellow);
        g.fillOval((int) (s.x - radius),(int) (s.y - radius),radius,radius);
    }

    //Check if this waypoint is collected, given the position of the ship.
    public boolean checkCollected(Vector2d a_pos, int a_radius)
    {
        double xd = s.x - a_pos.x;
        double yd = s.y - a_pos.y;
        double d = Math.sqrt(xd*xd+yd*yd);

        return d<(a_radius+this.radius);
    }

    //Sets if this waypoint is collected.
    public void setCollected(boolean coll)
    {
        if(!collected)
        {
            collected = coll;
            m_appletGame.waypointCollected();
        }
    }

    //GETTTERS
    public boolean isCollected() {return this.collected;}

    //SETTERS

    public void reset()
    {
        //Nothing to do here.
        this.collected = false;
    }


    @Override
    public boolean equals(Object a_other)
    {
        AppletWaypoint waypoint = (AppletWaypoint) a_other;
        if(this.s.x == waypoint.s.x && this.s.y == waypoint.s.y)
            return true;
        return false;
    }

    @Override
    public int hashCode()
    {
        return 100000*(100+(int)this.s.y) + (10000+(int)this.s.x);
    }

}
