package web;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.io.*;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 24/01/12
 * <p><applet archive="sites/default/files/web/ptsp_game.jar" code="web.PTSPApplet.class" height="367" title="Java" width="228"></applet></p>
 */
public class PTSPApplet extends JApplet implements KeyListener, ActionListener, Runnable {

    private Thread thread=new Thread(this);
    private boolean threadActivated=false;
    private boolean isRunning=false;

    //Delay in milliseconds between screenshots.
    final int DELAY = 16;

    //Applet objects
    private AppletGame m_ptspGame;
    private AppletView m_appletView;

    //Thrust pressed.
    private boolean m_thrust;

    //Turn.
    private int m_turn;

    //Reset button
    private JButton m_jbStop;
    private JButton m_jbStart;

    //Panels
    private JPanel m_controls;

    //Level selector
    private JComboBox m_levelSel;
    private HashMap<String,String> m_levelNames;
    private HashMap<String,Integer> m_levelIds;

    //Stream
    private InputStream m_stream;

    //Can start
    private boolean m_canStart;

    //Can start
    private boolean m_resultSent;

    //User id who is playing this, and username
    private int m_userId;
    private String m_username;

    //Map id being played.
    private int m_mapId;


    public void init()
    {
        try
        {
            initLevels();

            m_username = this.getParameter("Username");
            String userId = this.getParameter("UserId");
            m_userId = Integer.parseInt(userId);

            //Some initializations
            m_thrust = false;
            m_turn = 0;
            m_canStart = false;
            m_resultSent = false;

            //Panel and controls.
		    m_controls = new JPanel(new GridLayout(1,1));
		    JPanel buttons = new JPanel(new GridLayout(2,2));
            buttons.add(new JLabel("Select the level to play and press 'Start' "));
            buttons.add(m_levelSel);
		    m_jbStop = new JButton("Stop");
		    m_jbStart = new JButton("Start");
            m_jbStop.setEnabled(false);
		    buttons.add(m_jbStop);
            buttons.add(m_jbStart);
		    m_jbStop.addActionListener(this);
            m_jbStart.addActionListener(this);
            m_levelSel.addActionListener(this);

            m_controls.add(buttons);

            //Read map an start game:
            String mapName = "/ptsp_map01.map";
            m_mapId = 1;
            createGame(mapName);

            //Show the things in the applet.
            this.getContentPane().setLayout(new BorderLayout());
            this.getContentPane().add(m_appletView,"Center");
            this.getContentPane().add(m_controls,"North");
            this.setSize(this.getPreferredSize());
            this.addKeyListener(this);
            this.setVisible(true);


        }catch(Exception e)
        {
            e.printStackTrace();
        }
    }

    private void initLevels()
    {
        m_levelSel = new JComboBox();
        m_levelSel.addItem("Map 01");
        m_levelSel.addItem("Map 02");
        m_levelSel.addItem("Map 08");
        m_levelSel.addItem("Map 19");
        m_levelSel.addItem("Map 24");
        m_levelSel.addItem("Map 35");
        m_levelSel.addItem("Map 40");
        m_levelSel.addItem("Map 45");
        m_levelSel.addItem("Map 56");
        m_levelSel.addItem("Map 61");

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
            m_appletView = new AppletView(m_ptspGame, size, new java.awt.Dimension(625,610));
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
            System.out.print(" ... File read ok.");
            m_ptspGame.readMap(m_stream);
            System.out.println(" Waypoints: " + m_ptspGame.getNumWaypoints());
            m_appletView.reset();
            Dimension size = new Dimension(m_ptspGame.getMap().getMapChar().length, m_ptspGame.getMap().getMapChar()[0].length);
            m_appletView.setMapSize(size);
        }
    }

    public void reset()
    {
        //Some initializations
        m_thrust = false;
        m_turn = 0;
        m_ptspGame.reset();
        m_resultSent = false;
    }

    public void start()
    {
        if(!threadActivated)
        {
            thread=new Thread(this);
            threadActivated=true;
            thread.start();
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
            while(threadActivated && !m_ptspGame.hasEnded())
            {
                long then = System.currentTimeMillis();
                if(m_canStart)
                {
                    int stepAction = framework.core.Controller.getActionFromInput(m_thrust, m_turn);
                    m_ptspGame.stepRun(stepAction);
                }

                try
                {
                    long now = System.currentTimeMillis();
                    int remaining = (int) Math.max(0, this.DELAY - (now-then));     //To adjust to the proper framerate.
                    Thread.sleep(remaining);
                }
                catch(InterruptedException e)
                {
                    //e.printStackTrace();
                }

                m_appletView.repaint();

                if(m_ptspGame.hasEnded() && !m_resultSent)
                {
                    m_resultSent = true;
                    commitResults();
                }

            }
	}

    private void commitResults()
    {
        try
        {
            //Save to the data base.
            String phpRoute = "http://cseepgdp2.essex.ac.uk/save_play_c.php?"; //"http://localhost/save_play.php?"; //"http://ptsp-game.net/save_play.php?";
            String result=String.format(phpRoute + "user_id=%d&map_id=%d&waypoints=%d&time_spent=%d&c=cig12",
                    m_userId, m_mapId, m_ptspGame.getWaypointsCollected(), m_ptspGame.getTotalTime());
            //System.out.println(result);
            new URL(result).openStream();

            //Send the file to the server.
            ArrayList<Integer> actions = m_ptspGame.getShip().getActionList();
            String filename = m_mapId + "_" + m_ptspGame.getWaypointsCollected() + "_" + m_ptspGame.getTotalTime() + ".txt";
            new UploaderExample().upload(m_username, filename, m_ptspGame.getWaypointsCollected(), m_ptspGame.getTotalTime(), actions);
        }
        catch(Exception err){System.out.println(err.toString());}

    }

    public void actionPerformed(ActionEvent e)
    {
        if(e.getSource() == m_jbStop)
		{
            stop();
            reset();
            m_jbStart.setEnabled(true);
            m_levelSel.setEnabled(true);
            m_jbStop.setEnabled(false);
            m_canStart = false;
            m_appletView.setStartPressed(false);
            m_appletView.reset();
            this.requestFocusInWindow();
        }
        else if(e.getSource() == m_jbStart)
        {
            start();
            m_canStart = true;
            m_jbStart.setEnabled(false);
            m_levelSel.setEnabled(false);
            m_jbStop.setEnabled(true);
            m_appletView.setStartPressed(true);
		    this.requestFocusInWindow();
        }
        else if(e.getSource() == m_levelSel)
        {
            String selectedKey = (String) m_levelSel.getSelectedItem();
            String mapFileName = m_levelNames.get(selectedKey);
            m_mapId = m_levelIds.get(selectedKey);

            //System.out.println("MAP: " + mapFileName);
            readMap(mapFileName);
		    this.requestFocusInWindow();
        }
    }


    public void keyTyped(KeyEvent e) {
    }

    public void keyPressed(KeyEvent e) {
        int key = e.getKeyCode();
        if (key == KeyEvent.VK_UP) {
            m_thrust = true;
        }
        if (key == KeyEvent.VK_LEFT) {
            m_turn = -1;
        }
        if (key == KeyEvent.VK_RIGHT) {
            m_turn = 1;
        }
    }

    public void keyReleased(KeyEvent e) {
        int key = e.getKeyCode();
        if (key == KeyEvent.VK_UP) {
            m_thrust = false;
        }
        if (key == KeyEvent.VK_LEFT) {
            m_turn = 0;
        }
        if (key == KeyEvent.VK_RIGHT) {
            m_turn = 0;
        }
    }
}
