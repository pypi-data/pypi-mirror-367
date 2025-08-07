#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* swarm.c */
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

#include "petscdmswarm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmvectorgetfield_ DMSWARMVECTORGETFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmvectorgetfield_ dmswarmvectorgetfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmvectordefinefield_ DMSWARMVECTORDEFINEFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmvectordefinefield_ dmswarmvectordefinefield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcreatemassmatrixsquare_ DMSWARMCREATEMASSMATRIXSQUARE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcreatemassmatrixsquare_ dmswarmcreatemassmatrixsquare
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcreateglobalvectorfromfield_ DMSWARMCREATEGLOBALVECTORFROMFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcreateglobalvectorfromfield_ dmswarmcreateglobalvectorfromfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmdestroyglobalvectorfromfield_ DMSWARMDESTROYGLOBALVECTORFROMFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmdestroyglobalvectorfromfield_ dmswarmdestroyglobalvectorfromfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcreatelocalvectorfromfield_ DMSWARMCREATELOCALVECTORFROMFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcreatelocalvectorfromfield_ dmswarmcreatelocalvectorfromfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmdestroylocalvectorfromfield_ DMSWARMDESTROYLOCALVECTORFROMFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmdestroylocalvectorfromfield_ dmswarmdestroylocalvectorfromfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarminitializefieldregister_ DMSWARMINITIALIZEFIELDREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarminitializefieldregister_ dmswarminitializefieldregister
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmfinalizefieldregister_ DMSWARMFINALIZEFIELDREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmfinalizefieldregister_ dmswarmfinalizefieldregister
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsetlocalsizes_ DMSWARMSETLOCALSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsetlocalsizes_ dmswarmsetlocalsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsetcelldm_ DMSWARMSETCELLDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsetcelldm_ dmswarmsetcelldm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmgetcelldm_ DMSWARMGETCELLDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmgetcelldm_ dmswarmgetcelldm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmgetlocalsize_ DMSWARMGETLOCALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmgetlocalsize_ dmswarmgetlocalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmgetsize_ DMSWARMGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmgetsize_ dmswarmgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmregisterpetscdatatypefield_ DMSWARMREGISTERPETSCDATATYPEFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmregisterpetscdatatypefield_ dmswarmregisterpetscdatatypefield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmaddpoint_ DMSWARMADDPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmaddpoint_ dmswarmaddpoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmaddnpoints_ DMSWARMADDNPOINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmaddnpoints_ dmswarmaddnpoints
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmremovepoint_ DMSWARMREMOVEPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmremovepoint_ dmswarmremovepoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmremovepointatindex_ DMSWARMREMOVEPOINTATINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmremovepointatindex_ dmswarmremovepointatindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcopypoint_ DMSWARMCOPYPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcopypoint_ dmswarmcopypoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmmigrate_ DMSWARMMIGRATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmmigrate_ dmswarmmigrate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcollectviewcreate_ DMSWARMCOLLECTVIEWCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcollectviewcreate_ dmswarmcollectviewcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmcollectviewdestroy_ DMSWARMCOLLECTVIEWDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmcollectviewdestroy_ dmswarmcollectviewdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsetpointcoordinatesrandom_ DMSWARMSETPOINTCOORDINATESRANDOM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsetpointcoordinatesrandom_ dmswarmsetpointcoordinatesrandom
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmsettype_ DMSWARMSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmsettype_ dmswarmsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmgetcellswarm_ DMSWARMGETCELLSWARM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmgetcellswarm_ dmswarmgetcellswarm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmswarmrestorecellswarm_ DMSWARMRESTORECELLSWARM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmswarmrestorecellswarm_ dmswarmrestorecellswarm
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmswarmvectorgetfield_(DM dm, char *fieldname, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmVectorGetField(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for fieldname */
*ierr = PetscStrncpy(fieldname, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, fieldname, cl0);
}
PETSC_EXTERN void  dmswarmvectordefinefield_(DM dm, char fieldname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for fieldname */
  FIXCHAR(fieldname,cl0,_cltmp0);
*ierr = DMSwarmVectorDefineField(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(fieldname,_cltmp0);
}
PETSC_EXTERN void  dmswarmcreatemassmatrixsquare_(DM dmCoarse,DM dmFine,Mat *mass, int *ierr)
{
CHKFORTRANNULLOBJECT(dmCoarse);
CHKFORTRANNULLOBJECT(dmFine);
PetscBool mass_null = !*(void**) mass ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mass);
*ierr = DMSwarmCreateMassMatrixSquare(
	(DM)PetscToPointer((dmCoarse) ),
	(DM)PetscToPointer((dmFine) ),mass);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mass_null && !*(void**) mass) * (void **) mass = (void *)-2;
}
PETSC_EXTERN void  dmswarmcreateglobalvectorfromfield_(DM dm, char fieldname[],Vec *vec, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
/* insert Fortran-to-C conversion for fieldname */
  FIXCHAR(fieldname,cl0,_cltmp0);
*ierr = DMSwarmCreateGlobalVectorFromField(
	(DM)PetscToPointer((dm) ),_cltmp0,vec);
  FREECHAR(fieldname,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  dmswarmdestroyglobalvectorfromfield_(DM dm, char fieldname[],Vec *vec, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
/* insert Fortran-to-C conversion for fieldname */
  FIXCHAR(fieldname,cl0,_cltmp0);
*ierr = DMSwarmDestroyGlobalVectorFromField(
	(DM)PetscToPointer((dm) ),_cltmp0,vec);
  FREECHAR(fieldname,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  dmswarmcreatelocalvectorfromfield_(DM dm, char fieldname[],Vec *vec, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
/* insert Fortran-to-C conversion for fieldname */
  FIXCHAR(fieldname,cl0,_cltmp0);
*ierr = DMSwarmCreateLocalVectorFromField(
	(DM)PetscToPointer((dm) ),_cltmp0,vec);
  FREECHAR(fieldname,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  dmswarmdestroylocalvectorfromfield_(DM dm, char fieldname[],Vec *vec, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
/* insert Fortran-to-C conversion for fieldname */
  FIXCHAR(fieldname,cl0,_cltmp0);
*ierr = DMSwarmDestroyLocalVectorFromField(
	(DM)PetscToPointer((dm) ),_cltmp0,vec);
  FREECHAR(fieldname,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  dmswarminitializefieldregister_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmInitializeFieldRegister(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmfinalizefieldregister_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmFinalizeFieldRegister(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmsetlocalsizes_(DM dm,PetscInt *nlocal,PetscInt *buffer, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmSetLocalSizes(
	(DM)PetscToPointer((dm) ),*nlocal,*buffer);
}
PETSC_EXTERN void  dmswarmsetcelldm_(DM dm,DM dmcell, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(dmcell);
*ierr = DMSwarmSetCellDM(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((dmcell) ));
}
PETSC_EXTERN void  dmswarmgetcelldm_(DM dm,DM *dmcell, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmcell_null = !*(void**) dmcell ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmcell);
*ierr = DMSwarmGetCellDM(
	(DM)PetscToPointer((dm) ),dmcell);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmcell_null && !*(void**) dmcell) * (void **) dmcell = (void *)-2;
}
PETSC_EXTERN void  dmswarmgetlocalsize_(DM dm,PetscInt *nlocal, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(nlocal);
*ierr = DMSwarmGetLocalSize(
	(DM)PetscToPointer((dm) ),nlocal);
}
PETSC_EXTERN void  dmswarmgetsize_(DM dm,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(n);
*ierr = DMSwarmGetSize(
	(DM)PetscToPointer((dm) ),n);
}
PETSC_EXTERN void  dmswarmregisterpetscdatatypefield_(DM dm, char fieldname[],PetscInt *blocksize,PetscDataType *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for fieldname */
  FIXCHAR(fieldname,cl0,_cltmp0);
*ierr = DMSwarmRegisterPetscDatatypeField(
	(DM)PetscToPointer((dm) ),_cltmp0,*blocksize,*type);
  FREECHAR(fieldname,_cltmp0);
}
PETSC_EXTERN void  dmswarmaddpoint_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmAddPoint(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmaddnpoints_(DM dm,PetscInt *npoints, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmAddNPoints(
	(DM)PetscToPointer((dm) ),*npoints);
}
PETSC_EXTERN void  dmswarmremovepoint_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmRemovePoint(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmremovepointatindex_(DM dm,PetscInt *idx, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmRemovePointAtIndex(
	(DM)PetscToPointer((dm) ),*idx);
}
PETSC_EXTERN void  dmswarmcopypoint_(DM dm,PetscInt *pi,PetscInt *pj, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmCopyPoint(
	(DM)PetscToPointer((dm) ),*pi,*pj);
}
PETSC_EXTERN void  dmswarmmigrate_(DM dm,PetscBool *remove_sent_points, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmMigrate(
	(DM)PetscToPointer((dm) ),*remove_sent_points);
}
PETSC_EXTERN void  dmswarmcollectviewcreate_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmCollectViewCreate(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmcollectviewdestroy_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmCollectViewDestroy(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmswarmsetpointcoordinatesrandom_(DM dm,PetscInt *Npc, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmSetPointCoordinatesRandom(
	(DM)PetscToPointer((dm) ),*Npc);
}
PETSC_EXTERN void  dmswarmsettype_(DM dm,DMSwarmType *stype, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSwarmSetType(
	(DM)PetscToPointer((dm) ),*stype);
}
PETSC_EXTERN void  dmswarmgetcellswarm_(DM sw,PetscInt *cellID,DM cellswarm, int *ierr)
{
CHKFORTRANNULLOBJECT(sw);
CHKFORTRANNULLOBJECT(cellswarm);
*ierr = DMSwarmGetCellSwarm(
	(DM)PetscToPointer((sw) ),*cellID,
	(DM)PetscToPointer((cellswarm) ));
}
PETSC_EXTERN void  dmswarmrestorecellswarm_(DM sw,PetscInt *cellID,DM cellswarm, int *ierr)
{
CHKFORTRANNULLOBJECT(sw);
CHKFORTRANNULLOBJECT(cellswarm);
*ierr = DMSwarmRestoreCellSwarm(
	(DM)PetscToPointer((sw) ),*cellID,
	(DM)PetscToPointer((cellswarm) ));
}
#if defined(__cplusplus)
}
#endif
