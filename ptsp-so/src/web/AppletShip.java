package web;

import framework.core.*;
import framework.utils.Vector2d;

import java.awt.*;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 26/01/12
 */
public class AppletShip extends GameObject
{
    //Ship shape and physics
    public final int[] xp = {-2, 0, 2, 0};
    public final int[] yp = {2, -2, 2, 0};
    public final int[] xpThrust = {-2, 0, 2, 0};
    public final int[] ypThrust = {2, 3, 2, 0};
    public final static double steerStep = Math.PI / 60;// Math.PI / 45;
    public final static double loss = 0.99;
    public final int SHIP_RADIUS = 3;

    //game references
    private Controller m_shipController;
    private boolean m_started = false;

    //List of all the actions executed (for replies)
    private ArrayList<Integer> m_actionList;

    //movement
    private Vector2d m_potentialPosition;
    private Vector2d m_potentialSpeed;
    private boolean m_thrusting;
    private int m_turning;

    //Indicates if there was a collision at the last execution step.
    private boolean m_collisionLastStep;

    private final Color chassisColor = Color.cyan; //Color.cyan
    private final Color thrustColor = Color.green; //Color.red

    //Collision spheres
    private Vector2d m_collSphereRelative[]; //array in ship's local coordinates (relative)
    private Vector2d m_collSphere[];         //array in world coordinates (absolute)
    private Vector2d m_collPotentialSphere[];         //array in world coordinates in next step (absolute)

    private Vector2d m_startingPosition; //Starting position

    private AppletGame m_appGame;

    //Ship.
    public AppletShip(AppletGame a_game, Vector2d a_startPos)
    {
        m_startingPosition = a_startPos.copy();
        m_appGame = a_game;
        s = new Vector2d(a_startPos);
        ps = s.copy();
        v = new Vector2d(0,0);
        d = new Vector2d(0, -1);
        this.radius = SHIP_RADIUS;
        m_actionList = new ArrayList<Integer>();
        m_collisionLastStep = false;

        createCollSphere();
    }


    public void reset() {
        //Nothing to do here.
        s = new Vector2d(m_startingPosition);
        ps = s.copy();
        v = new Vector2d(0,0);
        d = new Vector2d(0, -1);
        this.radius = SHIP_RADIUS;
        m_actionList = new ArrayList<Integer>();
        m_collisionLastStep = false;

        createCollSphere();
    }


    public void createCollSphere()
    {
        int numPoints = 16;
        double angle = 2.0 * Math.PI / numPoints;
        m_collSphereRelative = new Vector2d[numPoints];
        m_collSphere = new Vector2d[numPoints];
        m_collPotentialSphere = new Vector2d[numPoints];

        m_collSphereRelative[0] = d.copy();
        m_collSphereRelative[0].mul(1.5*radius);
        m_collSphere[0] = new Vector2d();
        m_collPotentialSphere[0] = new Vector2d();
        for(int i = 1; i < m_collSphereRelative.length; ++i)
        {
            m_collSphereRelative[i] = m_collSphereRelative[i-1].copy();
            m_collSphereRelative[i].rotate(angle);
            m_collSphere[i] = new Vector2d();
            m_collPotentialSphere[i] = new Vector2d();
        }

        updateCollSphere();
    }

    private void updateCollPotentialSphere()
    {
        for(int i = 0; i < m_collSphereRelative.length; ++i)
        {
            m_collPotentialSphere[i].x = m_collSphereRelative[i].x + m_potentialPosition.x;
            m_collPotentialSphere[i].y = m_collSphereRelative[i].y + m_potentialPosition.y;
        }
    }

    private void updateCollSphere()
    {
        for(int i = 0; i < m_collSphereRelative.length; ++i)
        {
            m_collSphere[i].x = m_collPotentialSphere[i].x;
            m_collSphere[i].y = m_collPotentialSphere[i].y;
        }
    }

    //inits the ship given a controller.
    public void init(Controller a_shipController)
    {
        m_shipController = a_shipController;
    }

    //Call every cycle to update position and speed.
    public void update()
    {
        int actionId = m_appGame.getControllerAction();
        update(actionId);
    }

    //Updates position and manages collisions.
    public void update(int a_actionId)
    {

        if(!m_started)
        {
            if(a_actionId != Controller.ACTION_NO_FRONT)
            {
                m_started = true;
                m_appGame.go();
            }
            else
                return;
        }

        ps = s.copy();
        m_potentialPosition = s.copy();
        m_potentialSpeed = v.copy();
        m_thrusting = Controller.getThrust(a_actionId);
        m_turning = Controller.getTurning(a_actionId);

        d.rotate(m_turning * steerStep);
        if(m_thrusting)
            m_potentialSpeed.add(d, PTSPConstants.T * 0.05 / 2);
        m_potentialSpeed.mul(loss);
        m_potentialPosition.add(m_potentialSpeed);
        m_collisionLastStep = false;

        //Update the potential position of the collision sphere
        updateCollPotentialSphere();

        //Check for map boundaries:
        checkBoundaries();

        int coll = checkCollisions();
        if(coll != 0)
        {
            //There is collision
            m_collisionLastStep = true;
            if(coll == 1)
                v.x *= (-1);
            else
                v.y *= (-1);

            v.mul(PTSPConstants.COLLISION_SPEED_RED);
        }


        if(!m_collisionLastStep)
        {
            s = m_potentialPosition.copy();
            v = m_potentialSpeed.copy();

            //Update the position of the collision sphere
            updateCollSphere();

            // need to apply the wrap now...
            m_appGame.wrap(s);
        }


        m_actionList.add(a_actionId);

        //Check for visited waypoints.
        for(AppletWaypoint way : m_appGame.getWaypoints())
        {
            if(!way.isCollected())
            {
                boolean collected = way.checkCollected(this.s, this.radius);
                if(collected)
                {
                    way.setCollected(true);
                }
            }
        }
    }


    //Checks the boundaries of the map
    private void checkBoundaries()
    {

        if(m_potentialPosition.x > m_appGame.getMap().getMapChar().length-1)
        {
            m_potentialPosition.x = m_appGame.getMap().getMapChar().length-1;
        }
        else if(m_potentialPosition.x < 0)
        {
            m_potentialPosition.x = 0;
        }
        else if(m_potentialPosition.y > m_appGame.getMap().getMapChar()[0].length -1)
        {
            m_potentialPosition.y = m_appGame.getMap().getMapChar()[0].length -1;
        }
        else if(m_potentialPosition.y < 0)
        {
            m_potentialPosition.y = 0;
        }
    }

    //Collision estimation, checking all "angle points" of the ship.
    //0 no collision.
    //1 collision up/down
    //2 collision left/right
    private int checkCollisions()
    {

        for(int i = 0; i < m_collSphere.length; ++i)
        {
            Vector2d v = m_collPotentialSphere[i];
            int collision = checkCollInPos(v);
            if(collision != 0)
            {
                Vector2d vToColl = v.subtract(m_potentialPosition);
                vToColl.normalise();
                Vector2d velocity = m_potentialSpeed.copy();
                velocity.normalise();

                //This is to slide when in contact with walls instead of being stuck.
                double dotProduct = velocity.dot(vToColl);
                if(dotProduct > 0.5)
                    return collision;
            }
        }

        return 0;
    }

    private int checkCollInPos(Vector2d a_collPoint)
    {
        int xRound = (int)Math.round(a_collPoint.x);
        int yRound = (int)Math.round(a_collPoint.y);
        if(m_appGame.getMap().isObstacle(xRound, yRound))
        {
            if(m_appGame.getMap().isCollisionUpDown(xRound,yRound))
            {
                return 1;
            }
            else
            {
                return 2;
            }
        }
        return 0;
    }


    //Draws the ship.
    public void draw(Graphics2D g)
    {
        AffineTransform at = g.getTransform();
        g.translate(s.x, s.y);

        double rot = Math.atan2(d.y, d.x) + Controller.HALF_PI;
        g.rotate(rot);
        g.scale(radius, radius);
        g.setColor(chassisColor);
        g.fillPolygon(xp, yp, xp.length);
        if (m_thrusting) {
            g.setColor(thrustColor);
            g.fillPolygon(xpThrust, ypThrust, xpThrust.length);
        }

        g.setTransform(at);
        //printDebug(g);
    }

    private void printDebug(Graphics2D g)
    {
        //Collision sphere
        g.setColor(Color.yellow);
        for(int i = 0; i < m_collSphere.length; ++i)
        {
            Vector2d v = m_collSphere[i];
            g.drawOval((int) Math.round(v.x),(int) Math.round(v.y), 2, 2);
        }

        //CENTER OF THE SHIP  (real position in map).
        g.setColor(Color.red);
        g.drawOval((int) (s.x),(int) (s.y), 2, 2);
    }

    //Getters
    public ArrayList getActionList() {return m_actionList;}


}
