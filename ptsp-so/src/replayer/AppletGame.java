package replayer;

import framework.core.Controller;
import framework.core.Game;
import framework.core.GameObject;
import framework.core.PTSPConstants;
import framework.utils.Vector2d;

import java.awt.*;
import java.io.InputStream;
import java.util.LinkedList;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 26/01/12
 */
public class AppletGame
{
     //Objects of the game.
    private LinkedList<GameObject> m_gameObjects;

    //Map of the game.
    private AppletMap m_map;

    //Dimensions of the game.
    private Dimension m_size;


    //Ship of the game.
    private AppletShip m_ship;

    //Wrapper of the ship.
    private Vector2d m_wrapper = new Vector2d();

    //Graphics
    //private AppletView m_view;

    //Steps left for reaching a new waypoint
    private int m_stepsLeft;

    //Total time spent travelling through the map.
    public int m_totalTime;

    //Indicates if the game has started (ship has made a move).
    private boolean m_started;

    //Waypoints left to the end
    private int m_waypointsLeft;

    //Controller name.
    private String m_controllerName;

    //Indicates if the game is ended
    private boolean m_ended;

    //Controller action
    private int m_controllerAction;

    //This is the constructor for key controllers.
    public AppletGame(InputStream a_stream)
    {
        //Total time
        m_totalTime = m_controllerAction = 0;

        //It'll be started when the ship makes a move.
        m_started = m_ended = false;

        //Game objects container
        m_gameObjects = new LinkedList<GameObject>();

        //Create and read the map.
        m_map = new AppletMap(this, a_stream);

        //This is the number of steps allowed until reaching the next waypoint.
        m_stepsLeft = PTSPConstants.getStepsPerWaypoints(m_map.getNumWaypoints());

        //Initialize some variables
        m_size = new Dimension(m_map.getMapChar().length, m_map.getMapChar()[0].length);

        //Number of waypoints to be collected.
        m_waypointsLeft = m_map.getNumWaypoints();

        //Create the ship of the game.
        m_ship = new AppletShip(this, m_map.getStartingPoint());

        //Try to create the controller desired. If true, everything worked fine.
        /*m_agentController = new KeyController(this.getCopy());
        m_controllerName = "controllers.keycontroller.KeyController";
        m_ableToStart = true;

        m_ship.init(m_agentController);*/
        m_gameObjects.add(m_ship);

        //View of the game.
        //m_view = new AppletView(this, m_size, new java.awt.Dimension(625,610), m_map, m_ship);
       /* JEasyFrame frame = new JEasyFrame(m_view, "PTSP-Game: KeyController");
        if (m_view != null) {
            frame.addKeyListener((KeyController)m_agentController);
        } */
    }


    public void reset()
    {

        //This is the number of steps allowed until reaching the next waypoint.
        m_stepsLeft = PTSPConstants.getStepsPerWaypoints(m_map.getNumWaypoints());

        //Total time
        m_totalTime = m_controllerAction = 0;

        //It'll be started when the ship makes a move.
        m_started = m_ended = false;

        //reset the map.
        m_map.reset();

        //and the view
//m_view.reset();

        for(int i = 0; i < m_gameObjects.size(); ++i)
        {
            m_gameObjects.get(i).reset();
        }

        //Number of waypoints to be collected.
        m_waypointsLeft = m_map.getNumWaypoints();
    }


    public void readMap(InputStream a_stream)
    {
        reset();

        m_gameObjects.clear();

        //Create and read the map.
        m_map = new AppletMap(this, a_stream);

        //Initialize some variables
        m_size = new Dimension(m_map.getMapChar().length, m_map.getMapChar()[0].length);

        //Number of waypoints to be collected.
        m_waypointsLeft = m_map.getNumWaypoints();

        //Create the ship of the game.
        m_ship = new AppletShip(this, m_map.getStartingPoint());

        m_gameObjects.add(m_ship);


        //This is the number of steps allowed until reaching the next waypoint.
        m_stepsLeft = PTSPConstants.getStepsPerWaypoints(m_map.getNumWaypoints());

//m_view.setMapSize(m_size);
        //m_view.setSize(m_size);

        //View of the game.
        //m_view = new AppletView(this, m_size, new java.awt.Dimension(625,610), m_map, m_ship);
    }

    public void stepRun(int a_contAction)
    {
        m_controllerAction = a_contAction;
        if(m_controllerAction != Controller.ACTION_NO_FRONT)
        {
            m_started = true;
//m_view.setStartText(false);
        }

        synchronized (Game.class) {
            for (GameObject ob : m_gameObjects) {
                ob.update();
            }
        }

        //One steps left to the end.
        if(m_started)
        {
            m_stepsLeft--;
            m_totalTime++;
        }else
        {
//m_view.setStartText(true);
        }

        //Check for end of the game.
        if(m_waypointsLeft == 0 || m_stepsLeft <= 0)
            m_ended = true;

    }

    /**
     * Returns the number of waypoitns visited in this play.
     * @return the number of waypoitns visited in this play
     */
    public int getWaypointsVisited()
    {
        return (m_map.getNumWaypoints() - getWaypointsLeft());
    }

    /**
     * Returns the number of waypoints
     * @return the number of waypoints of the game.
     */
    public int getNumWaypoints() {return m_map.getNumWaypoints();}

    //Updates the game when a waypoint is collected.
    public void waypointCollected()
    {
        m_stepsLeft = PTSPConstants.getStepsPerWaypoints(m_map.getNumWaypoints());
        m_waypointsLeft--;
    }

    //Useful functions
    public void addGameObject(GameObject a_go)
    {
        m_gameObjects.add(a_go);
    }

    //Wrap method.
    public void wrap(Vector2d s) {
        m_wrapper.set(m_size.width / 2 - m_ship.s.x, m_size.height/ 2 - m_ship.s.y);
        s.add(m_wrapper);
        s.wrap(m_size.width*3, m_size.height*3);
        s.subtract(m_wrapper);
    }

    //Gets the waypoints collected
    public int getWaypointsCollected()
    {
        return m_map.getNumWaypoints()-m_waypointsLeft;
    }

    //Getters
    public LinkedList<GameObject> getGameObjects() {return m_gameObjects;}
    public AppletMap getMap() {return m_map;}
    public AppletShip getShip() {return m_ship;}
    public LinkedList<AppletWaypoint> getWaypoints() {return m_map.getWaypoints();}
    public int getWaypointsLeft() {return m_waypointsLeft;}
    public int getStepsLeft() {return m_stepsLeft;}
    public int getTotalTime() {return m_totalTime;}
    public boolean hasStarted() {return m_started;}
    public boolean hasEnded() {return m_ended;}
    public int getControllerAction() {return m_controllerAction;}

    //update methods.
    public void go(){m_started = true;}

}
