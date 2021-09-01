package replayer;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.io.InputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 24/01/12
 * <p><applet archive="sites/default/files/web/ptsp_game.jar" code="web.PTSPApplet.class" height="367" title="Java" width="228"></applet></p>
 */
public class PTSPApplet extends JApplet implements ActionListener, Runnable {

    private Thread thread=new Thread(this);
    private boolean threadActivated=false;
    private boolean isRunning=false;

    //Delay in milliseconds between screenshots.
    final int DELAY = 16;
    final int FASTER_DELAY = 5;

    //Applet objects
    private AppletGame m_ptspGame;
    private AppletView m_appletView;

    //Reset button
    //private JButton m_jbStop;
    private JButton m_jbStart;

    //Panels
    private JPanel m_controls;

    //Level selector
    private HashMap<String,String> m_levelNames;
    private HashMap<String,Integer> m_levelIds;

    //Stream
    private InputStream m_stream;

    //Can start
    private boolean m_canStart;

    //User id who is playing this, and username
    private int m_userId;
    private int m_waypoints;
    private int m_time;
    private int m_test;
    private int m_runId;
    private String m_username;

    //Map id being played.
    private int m_mapId;
    private int m_curAction;
    private int[] m_moves;
    

    public void init()
    {
        try
        {
            initLevels();

            m_username = this.getParameter("Username");
            String userId = this.getParameter("UserId");
            String humanPlayStr = this.getParameter("HumanPlay");
            String mapId = this.getParameter("MapId");
            String waypoints = this.getParameter("Waypoints");
            String time = this.getParameter("Time");
            String runId = this.getParameter("RunId");
            String test = this.getParameter("test");
            m_curAction = 0;
            
            m_userId = Integer.parseInt(userId);
            m_mapId = Integer.parseInt(mapId);
            m_waypoints = Integer.parseInt(waypoints);
            m_time = Integer.parseInt(time);
            m_runId = Integer.parseInt(runId);
            m_test = Integer.parseInt(test);

            boolean humanPlay = false;
            if(humanPlayStr.equals("1"))
                humanPlay = true;
            
            //Some initializations
            m_canStart = false;

            if(m_test == 0)
                m_moves =  new UploaderExample().download(this,m_username,humanPlay,m_mapId, m_waypoints, m_time);
            else
                m_moves =  new UploaderExample().downloadRunId(this,m_username,humanPlay,m_mapId, m_waypoints, m_time, m_runId);

            if(m_moves == null)
            {
                System.out.println("!Ups");
                return;
            }

            //Panel and controls.
		    m_controls = new JPanel(new GridLayout(1,1));
		    JPanel buttons = new JPanel(new GridLayout(1,1));
		    //m_jbStop = new JButton("Stop");
		    m_jbStart = new JButton("Start");
            //m_jbStop.setEnabled(false);
		    //buttons.add(m_jbStop);
            buttons.add(m_jbStart);
		    //m_jbStop.addActionListener(this);
            m_jbStart.addActionListener(this);

            m_controls.add(buttons);

            //Read map an start game:
            String mapName = "/ptsp_map";
            if(m_mapId < 10)
                mapName += "0" + m_mapId + ".map";
            else
                mapName += m_mapId + ".map";
            createGame(mapName);

            //Show the things in the applet.
            this.getContentPane().setLayout(new BorderLayout());
            this.getContentPane().add(m_appletView,"Center");
            this.getContentPane().add(m_controls,"North");
            this.setSize(this.getPreferredSize());
            this.setVisible(true);

        }catch(Exception e)
        {
            e.printStackTrace();
        }
    }

    private void initLevels()
    {
        m_levelNames = new HashMap<String, String>();
        m_levelNames.put("Map 01","/ptsp_map01.map");
        m_levelNames.put("Map 02","/ptsp_map02.map");
        m_levelNames.put("Map 08","/ptsp_map08.map");
        m_levelNames.put("Map 19","/ptsp_map19.map");
        m_levelNames.put("Map 24","/ptsp_map24.map");
        m_levelNames.put("Map 35","/ptsp_map35.map");
        m_levelNames.put("Map 40","/ptsp_map40.map");
        m_levelNames.put("Map 45","/ptsp_map45.map");
        m_levelNames.put("Map 56","/ptsp_map56.map");
        m_levelNames.put("Map 61","/ptsp_map61.map");


        m_levelIds = new HashMap<String, Integer>();
        m_levelIds.put("Map 01",1);
        m_levelIds.put("Map 02",2);
        m_levelIds.put("Map 08",8);
        m_levelIds.put("Map 19",19);
        m_levelIds.put("Map 24",24);
        m_levelIds.put("Map 35",35);
        m_levelIds.put("Map 40",40);
        m_levelIds.put("Map 45",45);
        m_levelIds.put("Map 56",56);
        m_levelIds.put("Map 61",61);
    }

    private void createGame(String a_mapFilename)
    {
        System.out.print("Reading map " + a_mapFilename);
        m_stream = this.getClass().getResourceAsStream(a_mapFilename);
        if(m_stream == null)
            System.out.println(" ... File not found.");
        else
        {
            System.out.println(" ... File read ok.");
            m_ptspGame = new AppletGame(m_stream);
            Dimension size = new Dimension(m_ptspGame.getMap().getMapChar().length, m_ptspGame.getMap().getMapChar()[0].length);
            m_appletView = new AppletView(m_ptspGame, size, new Dimension(858,727));
        }
    }

    private void readMap(String a_mapFilename)
    {
        System.out.print("Reading map " + a_mapFilename);
        m_stream = this.getClass().getResourceAsStream(a_mapFilename);
        if(m_stream == null)
            System.out.println(" ... File not found.");
        else
        {
            System.out.println(" ... File read ok.");
            m_ptspGame.readMap(m_stream);
            m_appletView.reset();
            Dimension size = new Dimension(m_ptspGame.getMap().getMapChar().length, m_ptspGame.getMap().getMapChar()[0].length);
            m_appletView.setMapSize(size);
        }
    }

    public void reset()
    {
        //Some initializations
        m_ptspGame.reset();
    }

    public void start()
    {
        if(!threadActivated)
        {
            thread=new Thread(this);
            threadActivated=true;
            thread.start();
            //isRunning = true;
            m_curAction = 0;
        }
    }


    public void stop()
    {
        if(isRunning)
        {
        	threadActivated=false;
        	isRunning=false;
            thread=null;
        }
    }

    public void run()
	{
       while(true)
       {
            while(threadActivated && !m_ptspGame.hasEnded())
            {
                long then = System.currentTimeMillis();
                if(m_canStart)
                {
                    int stepAction = m_moves[m_curAction];
                    m_curAction++;
                    //System.out.println(stepAction);
                    m_ptspGame.stepRun(stepAction);
                }

                m_appletView.repaint();
                long now = System.currentTimeMillis();

                try
                {

                    int remaining = (int) Math.max(0, this.FASTER_DELAY - (now-then));//To adjust to the proper framerate.
                    //Wait until de next cycle.
                    Thread.sleep(remaining);
                }
                catch(InterruptedException e)
                {
                    //e.printStackTrace();
                }

                
                if(m_ptspGame.hasEnded())
                {
                    m_jbStart.setEnabled(true);
                }

            }
            m_curAction = 0;
            m_appletView.repaint();
       }
	}

    private void commitResults()
    {
        try
        {
            //Save to the data base.
            String phpRoute = "http://cseepgdp2.essex.ac.uk/save_play.php?"; //"http://localhost/save_play.php?"; //"http://ptsp-game.net/save_play.php?";
            String result=String.format(phpRoute + "user_id=%d&map_id=%d&waypoints=%d&time_spent=%d",
                    m_userId, m_mapId, m_ptspGame.getWaypointsCollected(), m_ptspGame.getTotalTime());
            //System.out.println(result);
            new URL(result).openStream();

            //Send the file to the server.
            ArrayList<Integer> actions = m_ptspGame.getShip().getActionList();
            String filename = m_mapId + "_" + m_ptspGame.getWaypointsCollected() + "_" + m_ptspGame.getTotalTime() + ".txt";
            //new UploaderExample().upload(m_username, filename, m_ptspGame.getWaypointsCollected(), m_ptspGame.getTotalTime(), actions);
        }
        catch(Exception err){System.out.println(err.toString());}

    }

    public void actionPerformed(ActionEvent e)
    {
        /*if(e.getSource() == m_jbStop)
		{
            stop();
            reset();
            m_jbStart.setEnabled(true);
            m_jbStop.setEnabled(false);
            m_canStart = false;
            m_appletView.setStartPressed(false);
            m_appletView.reset();
            m_appletView.repaint();
            this.requestFocusInWindow();
        }
        else if(e.getSource() == m_jbStart)
        {
            start();
            m_canStart = true;
            m_curAction = 0;
            m_jbStart.setEnabled(false);
            m_jbStop.setEnabled(true);
            m_appletView.setStartPressed(true);
		    this.requestFocusInWindow();
        }  */

        if(e.getSource() == m_jbStart)
        {
            if(m_canStart)
            {
                stop();
                reset();
                m_jbStart.setEnabled(true);
                m_canStart = false;
                m_appletView.setStartPressed(false);
                m_appletView.reset();
                m_appletView.repaint();
            }


            m_ptspGame.m_totalTime = 0;
            m_curAction = 0;
            start();
            m_canStart = true;
            m_jbStart.setEnabled(false);
            m_appletView.setStartPressed(true);
            this.requestFocusInWindow();
        }


    }

}
