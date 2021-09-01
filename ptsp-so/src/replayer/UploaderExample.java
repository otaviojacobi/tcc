package replayer;

import java.applet.Applet;
import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 17/02/12
 */
public class UploaderExample
{

    public int[] download(Applet applet, String username, boolean humanPlay, int map_id, int a_waypointsCollected, int a_time) throws Exception
    {
        try {

            String filename;
            String route;

            if(humanPlay)
            {
                filename = map_id + "_" + a_waypointsCollected + "_" +  a_time + ".txt";
                route = "uploads-cig12/" + username + "/";

            }else
            {
                filename = a_waypointsCollected + "_" + a_time + "_" +  username + ".txt";
                route = "bestRoutes-cig12/" + map_id + "/" ;
            }

            String fullFilename = route + filename;

            //System.out.println(fullFilename);

            String contents;
            String line;
            URL url = null;
            try{
                url = new URL(applet.getCodeBase(), fullFilename);
            }
            catch(MalformedURLException e){
                e.printStackTrace();
            }
            try{
                InputStream in = url.openStream();
                BufferedReader bf = new BufferedReader
                        (new InputStreamReader(in));
                StringBuffer strBuff = new StringBuffer();
                while((line = bf.readLine()) != null){
                    strBuff.append(line + ":");
                }
                contents = strBuff.toString();


                String[] contentsArray = contents.split(":");
                ArrayList<Integer> movesArraylist = new ArrayList<Integer>();

                /*for(int i = 1; i < contentsArray.length; ++i)
                {
                    System.out.print ( " "  + contentsArray[i]);
                    if(i%20 == 0)
                        System.out.println();

                    moves[i-1] = Integer.parseInt(contentsArray[i]);
                }         */

                boolean started = false;
                for (int i=1; i<contentsArray.length; i++) {
                    int val = Integer.parseInt(contentsArray[i]);
                    if(started || val > 0)
                    {
                        started = true;
                        movesArraylist.add(val);
                    }
                }

                int moves[] = new int[movesArraylist.size()];
                for(int i = 0; i < moves.length; ++i)
                {
                    moves[i] = movesArraylist.get(i);
                    /*System.out.print ( " "  + moves[i]);
                    if(i%20 == 0)
                        System.out.println();  */
                }
                
                return moves;



            }
            catch(IOException e){
                e.printStackTrace();
            }catch(Exception e)
            {
                e.printStackTrace();
            }

            
            


        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;

    }

    public int[] downloadRunId(Applet applet, String username, boolean humanPlay, int map_id, int a_waypointsCollected, int a_time, int a_runId) throws Exception
    {
        try {

            String filename;
            String route;

            filename = map_id + "_" + a_runId + "_" + a_waypointsCollected + "_" +  a_time + ".txt";
            route = "jar/allRoutes/";

            String fullFilename = route + filename;

            //System.out.println(fullFilename);

            String contents;
            String line;
            URL url = null;
            try{
                url = new URL(applet.getCodeBase(), fullFilename);
            }
            catch(MalformedURLException e){
                e.printStackTrace();
            }
            try{
                InputStream in = url.openStream();
                BufferedReader bf = new BufferedReader
                        (new InputStreamReader(in));
                StringBuffer strBuff = new StringBuffer();
                while((line = bf.readLine()) != null){
                    strBuff.append(line + ":");
                }
                contents = strBuff.toString();


                String[] contentsArray = contents.split(":");
                ArrayList<Integer> movesArraylist = new ArrayList<Integer>();

                /*for(int i = 1; i < contentsArray.length; ++i)
                {
                    System.out.print ( " "  + contentsArray[i]);
                    if(i%20 == 0)
                        System.out.println();

                    moves[i-1] = Integer.parseInt(contentsArray[i]);
                }         */

                boolean started = false;
                for (int i=1; i<contentsArray.length; i++) {
                    int val = Integer.parseInt(contentsArray[i]);
                    if(started || val > 0)
                    {
                        started = true;
                        movesArraylist.add(val);
                    }
                }

                int moves[] = new int[movesArraylist.size()];
                for(int i = 0; i < moves.length; ++i)
                {
                    moves[i] = movesArraylist.get(i);
                    /*System.out.print ( " "  + moves[i]);
                    if(i%20 == 0)
                        System.out.println();  */
                }

                return moves;



            }
            catch(IOException e){
                e.printStackTrace();
            }catch(Exception e)
            {
                e.printStackTrace();
            }





        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;

    }

}

