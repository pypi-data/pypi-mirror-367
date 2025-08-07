#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexcreate.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplex.h"
#include "petscdmplextransform.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatedoublet_ DMPLEXCREATEDOUBLET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatedoublet_ dmplexcreatedoublet
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateboxmesh_ DMPLEXCREATEBOXMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateboxmesh_ dmplexcreateboxmesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatewedgeboxmesh_ DMPLEXCREATEWEDGEBOXMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatewedgeboxmesh_ dmplexcreatewedgeboxmesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetoptionsprefix_ DMPLEXSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetoptionsprefix_ dmplexsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatehexcylindermesh_ DMPLEXCREATEHEXCYLINDERMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatehexcylindermesh_ dmplexcreatehexcylindermesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatewedgecylindermesh_ DMPLEXCREATEWEDGECYLINDERMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatewedgecylindermesh_ dmplexcreatewedgecylindermesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatetpsmesh_ DMPLEXCREATETPSMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatetpsmesh_ dmplexcreatetpsmesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatespheremesh_ DMPLEXCREATESPHEREMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatespheremesh_ dmplexcreatespheremesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateballmesh_ DMPLEXCREATEBALLMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateballmesh_ dmplexcreateballmesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatereferencecell_ DMPLEXCREATEREFERENCECELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatereferencecell_ dmplexcreatereferencecell
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreate_ DMPLEXCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreate_ dmplexcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexbuildcoordinatesfromcelllistparallel_ DMPLEXBUILDCOORDINATESFROMCELLLISTPARALLEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexbuildcoordinatesfromcelllistparallel_ dmplexbuildcoordinatesfromcelllistparallel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatefromcelllistparallelpetsc_ DMPLEXCREATEFROMCELLLISTPARALLELPETSC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatefromcelllistparallelpetsc_ dmplexcreatefromcelllistparallelpetsc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatefromcellsectionparallel_ DMPLEXCREATEFROMCELLSECTIONPARALLEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatefromcellsectionparallel_ dmplexcreatefromcellsectionparallel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexbuildfromcelllist_ DMPLEXBUILDFROMCELLLIST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexbuildfromcelllist_ dmplexbuildfromcelllist
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexbuildcoordinatesfromcelllist_ DMPLEXBUILDCOORDINATESFROMCELLLIST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexbuildcoordinatesfromcelllist_ dmplexbuildcoordinatesfromcelllist
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatefromcelllistpetsc_ DMPLEXCREATEFROMCELLLISTPETSC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatefromcelllistpetsc_ dmplexcreatefromcelllistpetsc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatefromdag_ DMPLEXCREATEFROMDAG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatefromdag_ dmplexcreatefromdag
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatefromfile_ DMPLEXCREATEFROMFILE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatefromfile_ dmplexcreatefromfile
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateephemeral_ DMPLEXCREATEEPHEMERAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateephemeral_ dmplexcreateephemeral
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexcreatedoublet_(MPI_Fint * comm,PetscInt *dim,PetscBool *simplex,PetscBool *interpolate,PetscReal *refinementLimit,DM *newdm, int *ierr)
{
PetscBool newdm_null = !*(void**) newdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newdm);
*ierr = DMPlexCreateDoublet(
	MPI_Comm_f2c(*(comm)),*dim,*simplex,*interpolate,*refinementLimit,newdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newdm_null && !*(void**) newdm) * (void **) newdm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreateboxmesh_(MPI_Fint * comm,PetscInt *dim,PetscBool *simplex, PetscInt faces[], PetscReal lower[], PetscReal upper[], DMBoundaryType periodicity[],PetscBool *interpolate,PetscInt *localizationHeight,PetscBool *sparseLocalize,DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(faces);
CHKFORTRANNULLREAL(lower);
CHKFORTRANNULLREAL(upper);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateBoxMesh(
	MPI_Comm_f2c(*(comm)),*dim,*simplex,faces,lower,upper,periodicity,*interpolate,*localizationHeight,*sparseLocalize,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatewedgeboxmesh_(MPI_Fint * comm, PetscInt faces[], PetscReal lower[], PetscReal upper[], DMBoundaryType periodicity[],PetscBool *orderHeight,PetscBool *interpolate,DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(faces);
CHKFORTRANNULLREAL(lower);
CHKFORTRANNULLREAL(upper);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateWedgeBoxMesh(
	MPI_Comm_f2c(*(comm)),faces,lower,upper,periodicity,*orderHeight,*interpolate,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexsetoptionsprefix_(DM dm, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = DMPlexSetOptionsPrefix(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  dmplexcreatehexcylindermesh_(MPI_Fint * comm,DMBoundaryType *periodicZ,PetscInt *Nr,DM *dm, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateHexCylinderMesh(
	MPI_Comm_f2c(*(comm)),*periodicZ,*Nr,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatewedgecylindermesh_(MPI_Fint * comm,PetscInt *n,PetscBool *interpolate,DM *dm, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateWedgeCylinderMesh(
	MPI_Comm_f2c(*(comm)),*n,*interpolate,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatetpsmesh_(MPI_Fint * comm,DMPlexTPSType *tpstype, PetscInt extent[], DMBoundaryType periodic[],PetscBool *tps_distribute,PetscInt *refinements,PetscInt *layers,PetscReal *thickness,DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(extent);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateTPSMesh(
	MPI_Comm_f2c(*(comm)),*tpstype,extent,periodic,*tps_distribute,*refinements,*layers,*thickness,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatespheremesh_(MPI_Fint * comm,PetscInt *dim,PetscBool *simplex,PetscReal *R,DM *dm, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateSphereMesh(
	MPI_Comm_f2c(*(comm)),*dim,*simplex,*R,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreateballmesh_(MPI_Fint * comm,PetscInt *dim,PetscReal *R,DM *dm, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateBallMesh(
	MPI_Comm_f2c(*(comm)),*dim,*R,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatereferencecell_(MPI_Fint * comm,DMPolytopeType *ct,DM *refdm, int *ierr)
{
PetscBool refdm_null = !*(void**) refdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(refdm);
*ierr = DMPlexCreateReferenceCell(
	MPI_Comm_f2c(*(comm)),*ct,refdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! refdm_null && !*(void**) refdm) * (void **) refdm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreate_(MPI_Fint * comm,DM *mesh, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(mesh);
 PetscBool mesh_null = !*(void**) mesh ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mesh);
*ierr = DMPlexCreate(
	MPI_Comm_f2c(*(comm)),mesh);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mesh_null && !*(void**) mesh) * (void **) mesh = (void *)-2;
}
PETSC_EXTERN void  dmplexbuildcoordinatesfromcelllistparallel_(DM dm,PetscInt *spaceDim,PetscSF sfVert, PetscReal vertexCoords[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sfVert);
CHKFORTRANNULLREAL(vertexCoords);
*ierr = DMPlexBuildCoordinatesFromCellListParallel(
	(DM)PetscToPointer((dm) ),*spaceDim,
	(PetscSF)PetscToPointer((sfVert) ),vertexCoords);
}
PETSC_EXTERN void  dmplexcreatefromcelllistparallelpetsc_(MPI_Fint * comm,PetscInt *dim,PetscInt *numCells,PetscInt *numVertices,PetscInt *NVertices,PetscInt *numCorners,PetscBool *interpolate, PetscInt cells[],PetscInt *spaceDim, PetscReal vertexCoords[],PetscSF *vertexSF,PetscInt **verticesAdj,DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(cells);
CHKFORTRANNULLREAL(vertexCoords);
PetscBool vertexSF_null = !*(void**) vertexSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vertexSF);
CHKFORTRANNULLINTEGER(verticesAdj);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateFromCellListParallelPetsc(
	MPI_Comm_f2c(*(comm)),*dim,*numCells,*numVertices,*NVertices,*numCorners,*interpolate,cells,*spaceDim,vertexCoords,vertexSF,verticesAdj,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vertexSF_null && !*(void**) vertexSF) * (void **) vertexSF = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatefromcellsectionparallel_(MPI_Fint * comm,PetscInt *dim,PetscInt *numCells,PetscInt *numVertices,PetscInt *NVertices,PetscSection cellSection,PetscBool *interpolate, PetscInt cells[],PetscInt *spaceDim, PetscReal vertexCoords[],PetscSF *vertexSF,PetscInt **verticesAdj,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(cellSection);
CHKFORTRANNULLINTEGER(cells);
CHKFORTRANNULLREAL(vertexCoords);
PetscBool vertexSF_null = !*(void**) vertexSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vertexSF);
CHKFORTRANNULLINTEGER(verticesAdj);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateFromCellSectionParallel(
	MPI_Comm_f2c(*(comm)),*dim,*numCells,*numVertices,*NVertices,
	(PetscSection)PetscToPointer((cellSection) ),*interpolate,cells,*spaceDim,vertexCoords,vertexSF,verticesAdj,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vertexSF_null && !*(void**) vertexSF) * (void **) vertexSF = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexbuildfromcelllist_(DM dm,PetscInt *numCells,PetscInt *numVertices,PetscInt *numCorners, PetscInt cells[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(cells);
*ierr = DMPlexBuildFromCellList(
	(DM)PetscToPointer((dm) ),*numCells,*numVertices,*numCorners,cells);
}
PETSC_EXTERN void  dmplexbuildcoordinatesfromcelllist_(DM dm,PetscInt *spaceDim, PetscReal vertexCoords[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(vertexCoords);
*ierr = DMPlexBuildCoordinatesFromCellList(
	(DM)PetscToPointer((dm) ),*spaceDim,vertexCoords);
}
PETSC_EXTERN void  dmplexcreatefromcelllistpetsc_(MPI_Fint * comm,PetscInt *dim,PetscInt *numCells,PetscInt *numVertices,PetscInt *numCorners,PetscBool *interpolate, PetscInt cells[],PetscInt *spaceDim, PetscReal vertexCoords[],DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(cells);
CHKFORTRANNULLREAL(vertexCoords);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateFromCellListPetsc(
	MPI_Comm_f2c(*(comm)),*dim,*numCells,*numVertices,*numCorners,*interpolate,cells,*spaceDim,vertexCoords,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatefromdag_(DM dm,PetscInt *depth, PetscInt numPoints[], PetscInt coneSize[], PetscInt cones[], PetscInt coneOrientations[], PetscScalar vertexCoords[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(numPoints);
CHKFORTRANNULLINTEGER(coneSize);
CHKFORTRANNULLINTEGER(cones);
CHKFORTRANNULLINTEGER(coneOrientations);
CHKFORTRANNULLSCALAR(vertexCoords);
*ierr = DMPlexCreateFromDAG(
	(DM)PetscToPointer((dm) ),*depth,numPoints,coneSize,cones,coneOrientations,vertexCoords);
}
PETSC_EXTERN void  dmplexcreatefromfile_(MPI_Fint * comm, char filename[], char plexname[],PetscBool *interpolate,DM *dm, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for filename */
  FIXCHAR(filename,cl0,_cltmp0);
/* insert Fortran-to-C conversion for plexname */
  FIXCHAR(plexname,cl1,_cltmp1);
*ierr = DMPlexCreateFromFile(
	MPI_Comm_f2c(*(comm)),_cltmp0,_cltmp1,*interpolate,dm);
  FREECHAR(filename,_cltmp0);
  FREECHAR(plexname,_cltmp1);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreateephemeral_(DMPlexTransform tr, char prefix[],DM *dm, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tr);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = DMPlexCreateEphemeral(
	(DMPlexTransform)PetscToPointer((tr) ),_cltmp0,dm);
  FREECHAR(prefix,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
