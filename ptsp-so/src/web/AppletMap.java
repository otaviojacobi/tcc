package web;

import framework.core.Game;
import framework.core.Waypoint;
import framework.utils.File2String;
import framework.utils.Vector2d;

import javax.swing.*;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.InputStream;
import java.util.LinkedList;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 26/01/12
 */
public class AppletMap extends JComponent
{
    //Symbols for the ASCII map.
    public static final char EDGE = 'E';
    public static final char START = 'S';
    public static final char WAYPOINT = 'C';
    public static final char NIL = '.';

    //Map features
    private char m_mapChar[][];      //the map.
    private int m_height;              //height of the map.
    private int m_width;               //Width of the mao.
    private Vector2d m_startingPoint;   //Starting point in the map.

    //Waypoints of the map.
    private LinkedList<AppletWaypoint> m_waypoints;

    //Number of waypoints to collect/visit.
    private int m_numWaypoints;

    //Reference to the m_game.
    private AppletGame m_game;

    //Filename where this map is read from.
    private InputStream m_stream;

    public AppletMap(AppletGame a_game, InputStream a_stream)
    {
        this.m_game = a_game;
        m_stream = a_stream;
        m_startingPoint = new Vector2d();
        m_waypoints = new LinkedList<AppletWaypoint>();
        m_numWaypoints = 0;
        readMap();
    }

    public void reset()
    {
        //Nothing to do here, I think...
    }

    private void readMap()
    {
        String[][] fileData = File2String.readArray(m_stream);

        int x = 0, xInMap = 0;
        String[] line;
        while(x < fileData.length)
        {
            line = fileData[x]; //Get following line.

            String first = line[0];
            if(first.equalsIgnoreCase("type"))
            {
                //Ignore
            }else if(first.equalsIgnoreCase("height"))
            {
                String h = line[1];
                m_height = Integer.parseInt(h);
            }
            else if(first.equalsIgnoreCase("width"))
            {
                String w = line[1];
                m_width = Integer.parseInt(w);
            }
            else if(first.equalsIgnoreCase("map"))
            {
                //Ignore ... but time to create the map
                m_mapChar = new char[m_width][m_height];
            }
            else
            {
                //MAP INFORMATION
                String lineStr = line[0];
                int yInMap = 0;
                int yInFile = 0;
                while(yInMap < lineStr.length())
                {
                    char data = lineStr.charAt(yInFile);
                    //System.out.println(xInMap + "," + yInMap + ": " + data);
                    m_mapChar[yInMap][xInMap] = data;

                    processData(yInMap, xInMap, data);

                    ++yInMap;
                    ++yInFile;
                }
                ++xInMap;
            }

            ++x;
        }
    }

    private void processData(int x, int y, char data)
    {
        if(data == START)
        {
            m_startingPoint.x=x;
            m_startingPoint.y=y;
        }
        else if(data == WAYPOINT)
        {
            Vector2d newCol = new Vector2d(x,y);
            AppletWaypoint way = new AppletWaypoint(m_game, newCol);
            m_waypoints.add(way);
            m_game.addGameObject(way);
            m_numWaypoints++;
        }
    }


    public boolean isObstacle(int a_x, int a_y)
    {
        char inMap = m_mapChar[a_x][a_y];
        return isObstacle(inMap);
    }

    private boolean isObstacle(char data)
    {
        if(data == '@' || data == 'T' || data == '\u0000' || data == AppletMap.EDGE)
            return true;
        return false;
    }

    public boolean isCollisionUpDown(int a_x, int a_y)
    {
        int consUpDown = 1, consRightLeft = 1; //we suppose there is collision in (a_x, a_y)
        if(a_y+1 < m_mapChar[a_x].length)
        {
            consUpDown += isObstacle(m_mapChar[a_x][a_y+1])? 1:0;
        }
        if(a_y-1 >= 0)
        {
            consUpDown += isObstacle(m_mapChar[a_x][a_y-1])? 1:0;
        }

        if(a_x+1 < m_mapChar.length)
        {
            consRightLeft += isObstacle(m_mapChar[a_x+1][a_y])? 1:0;
        }
        if(a_x-1 >= 0)
        {
            consRightLeft += isObstacle(m_mapChar[a_x-1][a_y])? 1:0;
        }

        return consUpDown>consRightLeft;
    }

    public boolean checkObsFree(int a_orgX, int a_orgY, int a_destX, int a_destY)
    {
        double increment = 0.5;
        Vector2d dir = new Vector2d(a_destX - a_orgX, a_destY - a_orgY);
        double distance = dir.mag();
        dir.normalise();
        dir.mul(increment);
        double acum = increment;

        Vector2d pos = new Vector2d(a_orgX, a_orgY);
        while(acum < distance)
        {
            pos.add(dir);
            if(isObstacle(m_mapChar[(int)Math.round(pos.x)][(int)Math.round(pos.y)]))
                return false;
            acum += increment;
        }

        return true;
    }


    ///GETTERS
    public char[][] getMapChar() {return m_mapChar; }
    public Vector2d getStartingPoint() {return m_startingPoint.copy();}
    public LinkedList<AppletWaypoint> getWaypoints() {return m_waypoints;}
    public int getNumWaypoints() {return m_numWaypoints;}
    public int getMapHeight() {return m_height;}
    public int getMapWidth() {return m_width;}

    //SETTERS
    public void setMapChar(char[][] a_mapChar){m_mapChar = a_mapChar;}
    public void setHeight(int a_h) {m_height = a_h;}
    public void setWidth(int a_w) {m_width = a_w;}
    public void setStartingPoint(Vector2d a_sp) {m_startingPoint = a_sp;}
    public void setNumWaypoints(int a_numW) {m_numWaypoints = a_numW;}
    public void setGame(AppletGame a_game) {m_game = a_game;}

    //utils
    public void addWaypoint(AppletWaypoint a_way) {m_waypoints.add(a_way);}

}

