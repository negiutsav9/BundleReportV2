import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './Dashboard.css'
import {Bar, Pie} from 'react-chartjs-2'
import {Chart as ChartJS} from 'chart.js/auto'

function Dashboard() {

    const {state}= useLocation();
    const [title,setTitle] = useState(state.name);
    if(title === ""){
        setTitle("Bundle Report")
    }
    const [numIncluded, setNumIncluded] = useState(0);
    const [numOff, setNumOff] = useState(0);
    const [numData, setNumData] = useState(0);
    const [numOrg, setNumOrg] = useState(0);
    const [statTeam, setStatTeam] = useState({});
    const [statCategory, setStatCategory] = useState({});
    const [statType, setStatType] = useState({});

    const totalJIRA = numIncluded + numOff + numData + numOrg;
    
    useEffect(() => {
        // declare the async data fetching function
        const fetchData = async () => {
            // get the data from the api
            const response = await fetch('http://localhost:5000/stat',{
                method:'get',
                credentials:"include",
                headers:{
                    'Accept':'application/json',
                    'Content-Type':'application/json'
                },
                mode:'cors',
            });
            // convert the data to json
            const json = await response.json();
            //if done then redirect
            setNumIncluded(json['Bundle']['Included']);
            setNumOff(json['Bundle']['Off-Bundle']);
            setNumData(json['Bundle']['Data-Update']);
            setNumOrg(json['Bundle']['Organization']);
            setStatCategory(json['Category']);
            setStatTeam(json['Team']);
            setStatType(json['Type']);
        }
      
        // call the function
        fetchData()
          // make sure to catch any error
          .catch(console.error);
    }, [])

    const handleDownload = async () => {
        const res = await fetch('http://localhost:5000/download',{
            credentials:"include",
            headers:{
                'Accept':'application/json',
                'Content-Type':'application/json'
            },
            mode:'cors',
        });

        const blob = await res.blob();
        const newBlob = new Blob([blob]);

        const blobUrl = window.URL.createObjectURL(newBlob);

        const link = document.createElement('a');
        link.href = blobUrl;
        let file_name = title + ".xlsx"
        link.setAttribute('download', file_name);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);

        // clean up Url
        window.URL.revokeObjectURL(blobUrl);
    }

    const handleUpload = async () => {
        const res = await fetch('http://localhost:5000/upload',{
            credentials:"include",
            headers:{
                'Accept':'application/json',
                'Content-Type':'application/json'
            },
            mode:'cors',
        });
        console.log(res)
    }


    const chartType = {
        labels : Object.keys(statType),
        datasets: [
            {
              label: 'Bundle',
              backgroundColor: 'rgba(221,0,0,1)',
              borderColor: 'rgba(0,0,0,1)',
              borderWidth: 2,
              data: Object.values(statType),
            }
        ]
    }

    const chartCategory = {
        labels : Object.keys(statCategory),
        datasets: [
            {
              label: 'Bundle',
              backgroundColor: ['rgba(221,0,0,1)', 'rgba(221,221,0,1 )', 'rgba(121,121,121,1)'],
              borderColor: 'rgba(0,0,0,1)',
              borderWidth: 2,
              data: Object.values(statCategory)
            }
        ]
    }

    const chartTeam = {
        labels : Object.keys(statTeam),
        datasets: [
            {
              label: 'Bundle',
              backgroundColor: 'rgba(221,0,0,1)',
              borderColor: 'rgba(0,0,0,1)',
              borderWidth: 2,
              data: Object.values(statTeam),
              indexAxis:'y'
            }
        ]
    }

    return (
        <div className='dash-page'>
            <div className='Title'>
                Bundle Report Generator
            </div>
            <div className='dash-area'>
                <div className='dash-title'>
                    {title}
                </div>
                <button className='download-button' onClick={handleDownload}>
                    Download Bundle Report    
                </button>
                <button className='upload-button' onClick={handleUpload}>
                    Upload Bundle Report  
                </button>
                <div className='stat-type'>
                    <div className='type-header'>
                        Bundle <br/> Status
                    </div>
                    <div className="incl-bundle">
                        <div className="incl-num">
                            {(numIncluded*100/totalJIRA).toFixed(2)}%
                        </div>
                        <div className="incl-detail">
                            Included
                        </div>
                    </div>
                    <div className="off-bundle">
                        <div className="off-num">
                            {(numOff*100/totalJIRA).toFixed(2)}%
                        </div>
                        <div className="off-detail">
                            Off-Bundle
                        </div>
                    </div>
                    <div className="data">
                        <div className="data-num">
                            {(numData*100/totalJIRA).toFixed(2)}%
                        </div>
                        <div className="data-detail">
                            Data Update
                        </div>
                    </div>
                    <div className="org-update">
                        <div className="org-num">
                            {(numOrg*100/totalJIRA).toFixed(2)}%
                        </div>
                        <div className="org-detail">
                            Org Dept. Update
                        </div>
                    </div>
                </div>
                <div className='stat-crtype'>
                    <div className='type-header'>
                        Phire-CR Type
                    </div>
                </div>
                <div className='chart-type'>
                    <Bar
                        data={chartType}
                        options={{
                            title:{display:false},
                            legend:{display:false}
                        }}
                    />  
                </div>
                <div className='stat-teams'>
                    <div className='type-header'>
                        Team Distribution
                    </div>
                </div>
                <div className='chart-teams'>
                    <Bar
                        data={chartTeam}
                        options={{      
                            title:{display:false},
                            legend:{display:false}
                        }}
                    />  
                </div>
                <div className='stat-project'>
                    <div className='type-header'>
                        Project Type
                    </div>
                </div>
                <div className='chart-category'>
                    <Pie
                        data={chartCategory}
                        options={{
                            plugins:{
                                legend:{
                                    display:true,
                                    position:'left'
                                }
                            }
                        }}
                    />  
                </div> 
            </div>
        </div>
    );
}

export default Dashboard;